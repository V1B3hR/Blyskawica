"""Flamegraph profiling for Nethical threat detection system.

Production-safe profiling with flamegraph generation using:
- py-spy for minimal overhead (<1% CPU) in production
- cProfile for development fallback

Generates flamegraph SVG files for performance analysis.
"""

import cProfile
import importlib.util
import io
import logging
import pstats
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    PY_SPY_AVAILABLE = importlib.util.find_spec("py_spy") is not None
    PY_SPY_AVAILABLE = True
except ImportError:
    PY_SPY_AVAILABLE = False


class FlamegraphProfiler:
    """Production-safe profiling with flamegraph generation.
    
    Uses py-spy for minimal overhead (<1% CPU) in production.
    Falls back to cProfile for development when py-spy is not available.
    """  # noqa: W293

    def __init__(self, output_dir: str = "profiling_results"):
        """Initialize flamegraph profiler.
        
        Args:
            output_dir: Directory to store profiling results
        """  # noqa: W293
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
# noqa: W293
        if not PY_SPY_AVAILABLE:
            logger.warning(
                "py-spy not installed. Using cProfile instead (higher overhead). "
                "For production profiling, install with: pip install py-spy>=0.3.14"
            )
# noqa: W293
    def profile_sync(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> tuple[Any, Path]:
        """Profile synchronous function with cProfile.
        
        Args:
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Tuple of (function result, report file path)
        """  # noqa: W293
        profiler = cProfile.Profile()
        profiler.enable()
# noqa: W293
        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()
# noqa: W293
        # Save stats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        func_name = getattr(func, '__name__', 'unknown')
        stats_file = self.output_dir / f"profile_{func_name}_{timestamp}.stats"
        profiler.dump_stats(str(stats_file))
# noqa: W293
        # Generate text report
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(50)  # Top 50 functions
# noqa: W293
        report_file = self.output_dir / f"profile_{func_name}_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write(s.getvalue())
# noqa: W293
        logger.info(f"Profile saved to {report_file}")
# noqa: W293
        return result, report_file
# noqa: W293
    def profile_script(
        self,
        script_path: str,
        duration_seconds: int = 60,
        rate_hz: int = 100
    ) -> Path:
        """Profile a Python script using py-spy (if available).
        
        Args:
            script_path: Path to Python script to profile
            duration_seconds: Duration to profile for
            rate_hz: Sampling rate in Hz
            
        Returns:
            Path to generated flamegraph SVG
            
        Raises:
            RuntimeError: If py-spy is not installed
        """  # noqa: W293
        if not PY_SPY_AVAILABLE:
            raise RuntimeError(
                "py-spy not installed. Install with: pip install py-spy>=0.3.14"
            )
# noqa: W293
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_name = Path(script_path).stem
        output_file = self.output_dir / f"flamegraph_{script_name}_{timestamp}.svg"
# noqa: W293
        # Build py-spy command
        cmd = [
            'py-spy', 'record',
            '--format', 'flamegraph',
            '--output', str(output_file),
            '--duration', str(duration_seconds),
            '--rate', str(rate_hz),
            '--', 'python', script_path
        ]
# noqa: W293
        logger.info(f"Starting py-spy profiling for {duration_seconds}s...")
# noqa: W293
        # Run py-spy
        import subprocess
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration_seconds + 10)
# noqa: W293
            if result.returncode != 0:
                logger.error(f"py-spy failed: {result.stderr}")
                raise RuntimeError(f"py-spy profiling failed: {result.stderr}")
# noqa: W293
            logger.info(f"Flamegraph saved to {output_file}")
            return output_file
# noqa: W293
        except subprocess.TimeoutExpired:
            logger.error("py-spy profiling timed out")
            raise
# noqa: W293
    def profile_pid(
        self,
        pid: int,
        duration_seconds: int = 60,
        rate_hz: int = 100
    ) -> Path:
        """Profile a running process by PID using py-spy.
        
        Args:
            pid: Process ID to profile
            duration_seconds: Duration to profile for
            rate_hz: Sampling rate in Hz
            
        Returns:
            Path to generated flamegraph SVG
            
        Raises:
            RuntimeError: If py-spy is not installed
        """  # noqa: W293
        if not PY_SPY_AVAILABLE:
            raise RuntimeError(
                "py-spy not installed. Install with: pip install py-spy>=0.3.14"
            )
# noqa: W293
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"flamegraph_pid{pid}_{timestamp}.svg"
# noqa: W293
        # Build py-spy command
        cmd = [
            'py-spy', 'record',
            '--format', 'flamegraph',
            '--output', str(output_file),
            '--duration', str(duration_seconds),
            '--rate', str(rate_hz),
            '--pid', str(pid)
        ]
# noqa: W293
        logger.info(f"Starting py-spy profiling of PID {pid} for {duration_seconds}s...")
# noqa: W293
        # Run py-spy
        import subprocess
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration_seconds + 10)
# noqa: W293
            if result.returncode != 0:
                logger.error(f"py-spy failed: {result.stderr}")
                raise RuntimeError(f"py-spy profiling failed: {result.stderr}")
# noqa: W293
            logger.info(f"Flamegraph saved to {output_file}")
            return output_file
# noqa: W293
        except subprocess.TimeoutExpired:
            logger.error("py-spy profiling timed out")
            raise
# noqa: W293
    def generate_flamegraph_from_stats(
        self,
        stats_file: str
    ) -> Path | None:
        """Convert cProfile stats file to flamegraph.
        
        Note: This requires additional tools like flameprof or gprof2dot.
        This is a placeholder for future implementation.
        
        Args:
            stats_file: Path to .stats file from cProfile
            
        Returns:
            Path to generated SVG (or None if not implemented)
        """  # noqa: W293
        logger.warning(
            "Converting cProfile stats to flamegraph requires additional tools. "
            "Consider using py-spy directly for flamegraph generation."
        )
        return None


def profile_function(
    func: Callable,
    output_dir: str = "profiling_results",
    *args,
    **kwargs
) -> tuple[Any, Path]:
    """Convenience function to profile a function.
    
    Args:
        func: Function to profile
        output_dir: Directory for profiling results
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Tuple of (function result, report file path)
    """  # noqa: W293
    profiler = FlamegraphProfiler(output_dir=output_dir)
    return profiler.profile_sync(func, *args, **kwargs)
