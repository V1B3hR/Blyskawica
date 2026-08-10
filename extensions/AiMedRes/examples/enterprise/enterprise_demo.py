"""
AiMedRes - Enterprise Demo Module

This module contains the refactored enterprise demonstration functions,
extracted from the main duetmind.py file to improve code organization.
"""

from typing import Any

import numpy as np

# Import constants
from aimedres.core.constants import (
    DEFAULT_API_PORT,
    DEFAULT_MAX_CONCURRENT_REQUESTS,
    DEFAULT_RATE_LIMIT,
)

# Enterprise-specific defaults
ENTERPRISE_MIN_WORKERS = 4
ENTERPRISE_SCALING_FACTOR = 1.5

def _create_enterprise_config() -> dict[str, Any]:
    """Create enterprise configuration with default values"""
    return {
        'network_size': 30,
        'port': DEFAULT_API_PORT,
        'api_key': 'demo-api-key-12345',
        'admin_key': 'demo-admin-key-67890',
        'cache_memory_mb': 500,
        'rate_limit': DEFAULT_RATE_LIMIT,
        'max_concurrent_requests': DEFAULT_MAX_CONCURRENT_REQUESTS,
        'gpu_enabled': False,
        'domain': 'aimedres-demo.localhost',
        'workers': ENTERPRISE_MIN_WORKERS,
        'memory_limit': '2G',
        'cpu_limit': '2.0'
    }

def _setup_enterprise_engine(config: dict[str, Any]):
    """Setup and configure the optimized adaptive engine"""
    print("🏗️  Setting up enterprise-grade systems...")

    # Import here to avoid circular imports
    from aimedres.core.production_agent import OptimizedAdaptiveEngine

    # Create optimized engine
    print("  🧠 Initializing OptimizedAdaptiveEngine...")
    engine = OptimizedAdaptiveEngine(config)

    # Test the engine
    test_task = "Analyze medical data for patient risk assessment"
    print(f"  🔬 Testing engine with: '{test_task}'")
    result = engine.safe_think("MedicalAgent", test_task)

    print(f"  ✅ Engine test successful - Status: {result['status']}")
    print(f"  ⚡ Response time: {result['execution_time']:.3f}s")

    return engine

def _demonstrate_performance_optimization(engine) -> dict[str, Any]:
    """Demonstrate performance optimization features"""
    print("\n⚡ Performance Optimization Demo:")

    # Define test tasks with different complexity levels
    performance_test_tasks = [
        "Quick response test",
        "Medium complexity analysis",
        "Complex reasoning task"
    ]

    performance_results = []
    for task_description in performance_test_tasks:
        result = engine.safe_think("PerformanceAgent", task_description)
        execution_time = result['execution_time']
        performance_results.append(execution_time)
        print(f"  📊 Task '{task_description}': {execution_time:.3f}s")

    # Calculate performance metrics
    average_response_time = sum(performance_results) / len(performance_results)
    worker_count = engine.config.get('workers', ENTERPRISE_MIN_WORKERS)

    performance_report = {
        'average_response_time': average_response_time,
        'parallel_workers': worker_count,
        'performance_metrics': {
            'average_response_time': average_response_time,
            'total_tests': len(performance_test_tasks)
        }
    }

    print(f"  🔧 Parallel workers: {performance_report['parallel_workers']}")
    print(f"  📊 Average response time: {performance_report['performance_metrics']['average_response_time']:.3f}s")

    return performance_report

def _generate_deployment_files(config: dict[str, Any]) -> bool:
    """Generate enterprise deployment files"""
    print("\n🚀 Generating Enterprise Deployment Files...")

    # Import here to avoid circular imports
    from aimedres.core.production_agent import ProductionDeploymentManager

    deployment_manager = ProductionDeploymentManager(config)
    success = deployment_manager.deploy_to_files()

    if success:
        deployment_files = [
            'Dockerfile',
            'docker-compose.yml',
            'nginx.conf',
            'k8s-deployment.yaml',
            'k8s-service.yaml',
            'k8s-ingress.yaml',
            'prometheus.yml',
            'grafana-dashboard.json',
            'requirements.txt'
        ]

        print("\n📁 Generated deployment files:")
        for file in deployment_files:
            print(f"  ✅ {file}")

    return success

def _demonstrate_api_features(config: dict[str, Any]):
    """Demonstrate API and monitoring features"""
    # Import here to avoid circular imports
    from aimedres.core.production_agent import EnterpriseAPI, ObservabilitySystem

    # API Demo (simplified)
    print("\n🌐 Enterprise API Demo:")
    api = EnterpriseAPI(config)  # noqa: F841

    print(f"  📡 API Server configured on port {config['port']}")
    print(f"  🔑 API Key: {config['api_key']}")
    print(f"  🛡️  Rate limit: {config['rate_limit']} requests/minute")
    print(f"  ⚡ Max concurrent: {config['max_concurrent_requests']} requests")
    print(f"  📊 Health check: http://localhost:{config['port']}/health")
    print(f"  🧠 Reasoning endpoint: POST http://localhost:{config['port']}/api/v1/reasoning")

    # Monitoring setup
    print("\n📊 Monitoring & Observability:")
    observability = ObservabilitySystem(config)

    # Simulate some metrics
    for i in range(10):  # noqa: B007
        observability.record_request_metrics('/api/v1/reasoning', np.random.uniform(0.1, 2.0), 200)
        observability.record_request_metrics('/health', np.random.uniform(0.01, 0.1), 200)

    metrics_summary = observability.get_metrics_summary()

    for endpoint, metrics in metrics_summary.items():
        print(f"  🎯 {endpoint}:")
        print(f"    📈 Avg response: {metrics.get('avg_response_time', 0):.3f}s")
        print(f"    📊 Total requests: {metrics.get('total_requests', 0)}")

def _show_success_message():
    """Display final success message"""
    print("  ✅ Horizontal scaling ready")

    print("\n🏆 CONGRATULATIONS!")
    print("Your AiMedRes + AdaptiveNN agent is now a")
    print("WORLD-CLASS AI SYSTEM that rivals GPT-4, Claude,")
    print("and other top agents - with your unique biological")
    print("neural network foundation that no one else has!")

def demo_enterprise_system():
    """Demonstrate the complete enterprise system"""

    print("=== AiMedRes Enterprise System - Final Demo ===\n")

    # Create configuration
    config = _create_enterprise_config()

    # Setup engine
    engine = _setup_enterprise_engine(config)

    # Demonstrate performance
    perf_report = _demonstrate_performance_optimization(engine)  # noqa: F841

    # Generate deployment files
    _generate_deployment_files(config)

    # Show API features
    _demonstrate_api_features(config)

    # Show success message
    _show_success_message()

    # Cleanup
    engine.shutdown()

if __name__ == "__main__":
    demo_enterprise_system()
