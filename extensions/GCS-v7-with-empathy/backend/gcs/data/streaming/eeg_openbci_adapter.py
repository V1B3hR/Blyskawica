"""
EEG Streaming Adapter using OpenBCI (or simulation)

Provides real-time EEG data acquisition via BrainFlow
Falls back to synthetic data when hardware unavailable
"""

import numpy as np
import logging
import threading
import queue
import time
from typing import Optional, Dict
from dataclasses import dataclass


# Try to import BrainFlow
try:
    from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
    from brainflow.data_filter import DataFilter, FilterTypes
    BRAINFLOW_AVAILABLE = True
except ImportError:
    BRAINFLOW_AVAILABLE = False
    logging.warning("BrainFlow not available. Install: pip install brainflow")


@dataclass
class EEGStreamConfig:
    """Configuration for EEG streaming"""
    board_type: str = 'synthetic'  # 'synthetic', 'cyton', 'ganglion', etc.
    serial_port: str = ''
    sampling_rate: int = 250
    n_channels: int = 8
    window_size: float = 4.0  # seconds
    enable_filters: bool = True
    notch_freq: float = 60.0  # Hz (50 or 60)


class EEGStreamAdapter:
    """
    Adapter for real-time EEG streaming
    
    Supports:
    - OpenBCI boards via BrainFlow
    - Synthetic data generation for testing
    - Windowing and basic preprocessing
    """
    
    def __init__(self, config: EEGStreamConfig):
        """
        Args:
            config: EEGStreamConfig instance
        """
        self.config = config
        self.board = None
        self.is_streaming = False
        self.data_queue = queue.Queue(maxsize=100)
        self.stream_thread = None
        
        # Initialize board
        self._initialize_board()
        
        logging.info(f"EEG Stream Adapter initialized: {config.board_type}")
    
    def _initialize_board(self):
        """Initialize BrainFlow board"""
        if not BRAINFLOW_AVAILABLE or self.config.board_type == 'synthetic':
            logging.info("Using synthetic EEG stream")
            self.board = None
            return
        
        try:
            # Create board parameters
            params = BrainFlowInputParams()
            if self.config.serial_port:
                params.serial_port = self.config.serial_port
            
            # Map board type to BoardIds
            board_id_map = {
                'cyton': BoardIds.CYTON_BOARD,
                'ganglion': BoardIds.GANGLION_BOARD,
                'cyton_daisy': BoardIds.CYTON_DAISY_BOARD,
                'synthetic': BoardIds.SYNTHETIC_BOARD,
            }
            
            board_id = board_id_map.get(self.config.board_type, BoardIds.SYNTHETIC_BOARD)
            
            # Create board
            self.board = BoardShim(board_id, params)
            self.board.prepare_session()
            
            logging.info(f"BrainFlow board initialized: {self.config.board_type}")
            
        except Exception as e:
            logging.warning(f"Failed to initialize BrainFlow: {e}. Using synthetic data.")
            self.board = None
    
    def start_stream(self):
        """Start EEG data streaming"""
        if self.is_streaming:
            logging.warning("Stream already running")
            return
        
        self.is_streaming = True
        
        if self.board is not None:
            try:
                self.board.start_stream()
                logging.info("BrainFlow stream started")
            except Exception as e:
                logging.error(f"Failed to start BrainFlow stream: {e}")
                self.board = None
        
        # Start background thread
        self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.stream_thread.start()
        
        logging.info("EEG streaming started")
    
    def stop_stream(self):
        """Stop EEG data streaming"""
        if not self.is_streaming:
            return
        
        self.is_streaming = False
        
        if self.board is not None:
            try:
                self.board.stop_stream()
                logging.info("BrainFlow stream stopped")
            except Exception as e:
                logging.error(f"Error stopping stream: {e}")
        
        if self.stream_thread is not None:
            self.stream_thread.join(timeout=2.0)
        
        logging.info("EEG streaming stopped")
    
    def _stream_loop(self):
        """Background streaming loop"""
        while self.is_streaming:
            try:
                # Get data
                if self.board is not None:
                    # Real board data
                    data = self.board.get_board_data()
                    if data.size > 0:
                        # Extract EEG channels
                        eeg_channels = BoardShim.get_eeg_channels(self.board.board_id)
                        eeg_data = data[eeg_channels, :]
                        
                        # Apply filters if enabled
                        if self.config.enable_filters:
                            eeg_data = self._apply_filters(eeg_data)
                        
                        # Add to queue
                        if not self.data_queue.full():
                            self.data_queue.put(eeg_data)
                else:
                    # Synthetic data
                    n_samples = int(self.config.sampling_rate * 0.1)  # 100ms chunks
                    synthetic_data = np.random.randn(self.config.n_channels, n_samples) * 50
                    
                    if not self.data_queue.full():
                        self.data_queue.put(synthetic_data)
                
                time.sleep(0.05)  # 50ms sleep
                
            except Exception as e:
                logging.error(f"Error in stream loop: {e}")
                time.sleep(0.1)
    
    def _apply_filters(self, eeg_data: np.ndarray) -> np.ndarray:
        """Apply basic filtering to EEG data"""
        try:
            for ch in range(eeg_data.shape[0]):
                # Bandpass filter (1-50 Hz)
                DataFilter.perform_bandpass(
                    eeg_data[ch, :],
                    self.config.sampling_rate,
                    1.0, 50.0,
                    order=4,
                    filter_type=FilterTypes.BUTTERWORTH,
                    ripple=0
                )
                
                # Notch filter for line noise
                DataFilter.perform_bandstop(
                    eeg_data[ch, :],
                    self.config.sampling_rate,
                    self.config.notch_freq - 1,
                    self.config.notch_freq + 1,
                    order=4,
                    filter_type=FilterTypes.BUTTERWORTH,
                    ripple=0
                )
        except Exception as e:
            logging.warning(f"Error applying filters: {e}")
        
        return eeg_data
    
    def get_latest_window(self) -> Optional[np.ndarray]:
        """
        Get latest time window of EEG data
        
        Returns:
            EEG array of shape (channels, timesteps) or None if not enough data
        """
        if not self.is_streaming:
            return None
        
        # Collect data from queue
        all_data = []
        while not self.data_queue.empty():
            try:
                chunk = self.data_queue.get_nowait()
                all_data.append(chunk)
            except queue.Empty:
                break
        
        if not all_data:
            return None
        
        # Concatenate chunks
        combined = np.concatenate(all_data, axis=1)
        
        # Get window
        window_samples = int(self.config.window_size * self.config.sampling_rate)
        
        if combined.shape[1] < window_samples:
            # Not enough data yet
            return None
        
        # Return most recent window
        window = combined[:, -window_samples:]
        
        return window
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_stream()
        
        if self.board is not None:
            try:
                self.board.release_session()
            except Exception as e:
                logging.error(f"Error releasing board: {e}")


def create_eeg_adapter(config: Dict) -> EEGStreamAdapter:
    """
    Factory function to create EEG adapter from config
    
    Args:
        config: Configuration dictionary
    
    Returns:
        EEGStreamAdapter instance
    """
    streaming_config = config.get('simulation', {})
    
    stream_config = EEGStreamConfig(
        board_type=streaming_config.get('board_type', 'synthetic'),
        sampling_rate=streaming_config.get('synthetic_sample_rate', 250),
        n_channels=streaming_config.get('synthetic_eeg_channels', 8),
        window_size=4.0
    )
    
    return EEGStreamAdapter(stream_config)
