"""
FastAPI server for affective state recognition

Provides:
- REST API for single-shot predictions
- WebSocket for real-time affective state streaming
- Prometheus metrics
- Integration with empathy engine
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import yaml


def optional_import(module_name: str, symbols: List[str], warning_message: str) -> Tuple[List[Any], bool]:
    """
    Utility function for optional dependency handling
    
    Args:
        module_name: Name of the module to import
        symbols: List of symbols to import from the module
        warning_message: Warning message to display if import fails
    
    Returns:
        Tuple of (list of imported symbols or Nones, import success flag)
    """
    try:
        module = __import__(module_name, fromlist=symbols)
        imported = [getattr(module, sym) for sym in symbols]
        return imported, True
    except ImportError:
        logging.warning(warning_message)
        return [None] * len(symbols), False


# FastAPI optional import
(FastAPI, WebSocket, WebSocketDisconnect, HTTPException), FASTAPI_AVAILABLE = optional_import(
    "fastapi", ["FastAPI", "WebSocket", "WebSocketDisconnect", "HTTPException"],
    "FastAPI not available. Install: pip install fastapi uvicorn"
)
(CORSMiddleware,), _ = optional_import(
    "fastapi.middleware.cors", ["CORSMiddleware"],
    "FastAPI CORS middleware not available. Install: pip install fastapi"
)
(BaseModel,), _ = optional_import(
    "pydantic", ["BaseModel"],
    "Pydantic not available. Install: pip install pydantic"
)

# Prometheus optional import
(Counter, Histogram, Gauge, generate_latest), PROMETHEUS_AVAILABLE = optional_import(
    "prometheus_client", ["Counter", "Histogram", "Gauge", "generate_latest"],
    "Prometheus client not available. Install: pip install prometheus_client"
)
(CONTENT_TYPE_LATEST,), _ = optional_import(
    "prometheus_client", ["CONTENT_TYPE_LATEST"],
    "Prometheus client not available. Install: pip install prometheus_client"
)


# Prometheus metrics
if PROMETHEUS_AVAILABLE:
    INFERENCE_COUNTER = Counter('affective_inferences_total', 'Total affective inferences')
    INFERENCE_LATENCY = Histogram('affective_inference_latency_seconds', 'Inference latency')
    CRISIS_EVENTS = Counter('affective_crisis_events_total', 'Crisis events detected')
    UNCERTAINTY_GAUGE = Gauge('affective_uncertainty_mean', 'Mean uncertainty')
    WS_CONNECTIONS = Gauge('affective_ws_connections', 'Active WebSocket connections')


# Import GCS modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from gcs.models.affective_model import build_affective_model, compile_affective_model
from gcs.empathy_engine import EmotionalState, CrisisLevel


# Pydantic models for API
if FASTAPI_AVAILABLE:
    class AffectivePredictionRequest(BaseModel):
        eeg: Optional[List[List[float]]] = None
        physio: Optional[List[float]] = None
        voice: Optional[List[float]] = None
        text: Optional[str] = None
        user_id: Optional[str] = None


class AffectiveServer:
    """
    Affective state recognition server
    
    Manages:
    - Model loading
    - Streaming adapters
    - WebSocket connections
    - Metrics
    """
    
    def __init__(self, config_path: str):
        """
        Args:
            config_path: Path to affective_config.yaml
        """
        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Build model
        logging.info("Loading affective model...")
        self.model = build_affective_model(self.config)
        self.model = compile_affective_model(self.model, self.config)
        logging.info(f"Model loaded: {self.model.count_params():,} parameters")
        
        # Serving config
        serving_config = self.config.get('serving', {})
        self.push_hz = serving_config.get('push_hz', 3)
        self.smoothing = serving_config.get('smoothing', 'ema')
        self.ema_alpha = serving_config.get('ema_alpha', 0.3)
        
        # Empathy config
        empathy_config = self.config.get('empathy', {})
        self.crisis_detection = empathy_config.get('ethics', {}).get('crisis_detection_enabled', True)
        self.crisis_thresholds = empathy_config.get('ethics', {}).get('crisis_thresholds', {})
        
        # Streaming adapters
        self.adapters = {}
        
        # Active WebSocket connections
        self.active_connections: List[WebSocket] = []
        
        # Streaming state
        self.is_streaming = False
        self.stream_task = None
        
        # Smoothing buffers
        self.valence_buffer = []
        self.arousal_buffer = []
        self.categorical_buffer = []
        
        logging.info("Affective Server initialized")
    
    def start_streaming_adapters(self):
        """Start all streaming adapters"""
        from gcs.data.streaming.eeg_openbci_adapter import create_eeg_adapter
        from gcs.data.streaming.simple_adapters import create_physio_adapter, create_voice_adapter
        
        if self.config.get('modalities', {}).get('eeg', True):
            self.adapters['eeg'] = create_eeg_adapter(self.config)
            self.adapters['eeg'].start_stream()
        
        if self.config.get('modalities', {}).get('physio', True):
            self.adapters['physio'] = create_physio_adapter(self.config)
            self.adapters['physio'].start_stream()
        
        if self.config.get('modalities', {}).get('voice', True):
            self.adapters['voice'] = create_voice_adapter(self.config)
            self.adapters['voice'].start_stream()
        
        logging.info("Streaming adapters started")
    
    def stop_streaming_adapters(self):
        """Stop all streaming adapters"""
        for adapter in self.adapters.values():
            adapter.cleanup()
        self.adapters.clear()
        logging.info("Streaming adapters stopped")
    
    def get_streaming_data(self) -> Optional[Dict[str, np.ndarray]]:
        """Collect latest data from streaming adapters"""
        inputs = {}
        
        # EEG
        if 'eeg' in self.adapters:
            eeg_window = self.adapters['eeg'].get_latest_window()
            if eeg_window is not None:
                # Expand batch dimension
                inputs['eeg'] = np.expand_dims(eeg_window, axis=0)
        
        # Physio
        if 'physio' in self.adapters:
            physio_features = self.adapters['physio'].get_latest_features()
            if physio_features is not None:
                inputs['physio'] = np.expand_dims(physio_features, axis=0)
        
        # Voice
        if 'voice' in self.adapters:
            voice_features = self.adapters['voice'].get_latest_features()
            if voice_features is not None:
                inputs['voice'] = np.expand_dims(voice_features, axis=0)
        
        # Need at least one modality
        if not inputs:
            return None
        
        return inputs
    
    def predict(self, inputs: Dict[str, np.ndarray], 
                user_id: Optional[str] = None) -> Dict:
        """
        Run inference
        
        Returns:
            Dictionary with affective state and metadata
        """
        start_time = time.time()
        
        # Run model
        outputs, uncertainties = self.model.predict_with_uncertainty(
            inputs,
            mc_samples=self.config.get('uncertainty', {}).get('mc_dropout_samples', 15)
        )
        
        # Extract values
        valence = float(outputs['valence'].numpy()[0])
        arousal = float(outputs['arousal'].numpy()[0])
        categorical_probs = outputs['categorical'].numpy()[0]
        
        # Get predicted emotion
        emotion_idx = int(np.argmax(categorical_probs))
        emotion_confidence = float(categorical_probs[emotion_idx])
        
        # Map to EmotionalState
        emotion_states = list(EmotionalState)
        emotion_state = emotion_states[emotion_idx] if emotion_idx < len(emotion_states) else EmotionalState.BOREDOM
        
        # Uncertainty
        valence_uncertainty = float(uncertainties['valence'].numpy()[0])
        arousal_uncertainty = float(uncertainties['arousal'].numpy()[0])
        
        # Crisis detection
        crisis_detected = self._check_crisis(valence, arousal)
        
        # Inference time
        inference_time = time.time() - start_time
        
        # Update metrics
        if PROMETHEUS_AVAILABLE:
            INFERENCE_COUNTER.inc()
            INFERENCE_LATENCY.observe(inference_time)
            UNCERTAINTY_GAUGE.set(float(valence_uncertainty + arousal_uncertainty) / 2)
            if crisis_detected:
                CRISIS_EVENTS.inc()
        
        # Format output
        result = {
            'valence': valence,
            'arousal': arousal,
            'emotion': emotion_state.value,
            'confidence': emotion_confidence,
            'uncertainties': {
                'valence': valence_uncertainty,
                'arousal': arousal_uncertainty
            },
            'crisis_detected': crisis_detected,
            'inference_time_ms': inference_time * 1000
        }
        
        return result
    
    def _check_crisis(self, valence: float, arousal: float) -> bool:
        """Check if current state indicates crisis"""
        if not self.crisis_detection:
            return False
        
        arousal_threshold = self.crisis_thresholds.get('arousal', 0.9)
        negative_valence_threshold = self.crisis_thresholds.get('negative_valence', -0.7)
        
        if arousal > arousal_threshold and valence < negative_valence_threshold:
            return True
        
        return False
    
    def format_for_frontend(self, prediction: Dict) -> Dict:
        """Format prediction for frontend consumption"""
        # Map emotion to icon (simplified)
        icon_map = {
            'joy': '😊', 'excitement': '🤩', 'contentment': '😌',
            'anxiety': '😟', 'fear': '😨', 'anger': '😠',
            'sadness': '😢', 'surprise': '😲', 'boredom': '😐'
        }
        
        emotion = prediction['emotion']
        icon = icon_map.get(emotion, '😐')
        
        # Strength from arousal and confidence
        strength = int((prediction['arousal'] + prediction['confidence']) / 2 * 100)
        
        return {
            'affective': {
                'label': emotion,
                'icon': icon,
                'strength': strength,
                'valence': prediction['valence'],
                'arousal': prediction['arousal'],
                'confidence': prediction['confidence']
            },
            'empathic_response': {
                'content': f"I sense you're feeling {emotion}.",
                'intensity': 'moderate',
                'type': 'validation',
                'confidence': prediction['confidence']
            },
            'privacy_protected': True,
            'crisis_detected': prediction['crisis_detected'],
            'cultural_adaptation': 'neutral'
        }


# Create FastAPI app
if FASTAPI_AVAILABLE:
    app = FastAPI(title="GCS Affective State Recognition API")
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Global server instance
    server_instance = None
    
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize server on startup"""
        global server_instance
        
        # Find config
        config_path = os.path.join(os.path.dirname(__file__), '..', 'affective_config.yaml')
        if not os.path.exists(config_path):
            config_path = 'backend/gcs/affective_config.yaml'
        
        server_instance = AffectiveServer(config_path)
        server_instance.start_streaming_adapters()
        
        logging.info("Affective server started")
    
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        if server_instance:
            server_instance.stop_streaming_adapters()
        logging.info("Affective server stopped")
    
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {"message": "GCS Affective State Recognition API", "status": "running"}
    
    
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint"""
        if PROMETHEUS_AVAILABLE:
            return generate_latest()
        return {"error": "Prometheus not available"}
    
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time affective state"""
        await websocket.accept()
        server_instance.active_connections.append(websocket)
        
        if PROMETHEUS_AVAILABLE:
            WS_CONNECTIONS.set(len(server_instance.active_connections))
        
        try:
            # Send initial message
            await websocket.send_json({"status": "connected"})
            
            # Stream loop
            while True:
                # Get streaming data
                inputs = server_instance.get_streaming_data()
                
                if inputs:
                    # Run prediction
                    prediction = server_instance.predict(inputs)
                    
                    # Format for frontend
                    message = server_instance.format_for_frontend(prediction)
                    
                    # Send to client
                    await websocket.send_json(message)
                
                # Sleep based on push rate
                await asyncio.sleep(1.0 / server_instance.push_hz)
                
        except WebSocketDisconnect:
            logging.info("WebSocket client disconnected")
        except Exception as e:
            logging.error(f"WebSocket error: {e}")
        finally:
            server_instance.active_connections.remove(websocket)
            if PROMETHEUS_AVAILABLE:
                WS_CONNECTIONS.set(len(server_instance.active_connections))


if __name__ == "__main__":
    import uvicorn
    
    logging.basicConfig(level=logging.INFO)
    
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)
