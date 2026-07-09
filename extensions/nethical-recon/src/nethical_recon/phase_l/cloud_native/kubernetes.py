"""
Kubernetes Enhancements
Advanced Kubernetes configurations including Service Mesh and HPA
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class KubernetesConfig:
    """Kubernetes deployment configuration"""

    namespace: str
    replicas: int
    enable_service_mesh: bool
    enable_hpa: bool
    hpa_min_replicas: int
    hpa_max_replicas: int
    hpa_target_cpu: int
    enable_network_policies: bool
    enable_pod_security: bool


class KubernetesEnhancer:
    """
    Enhances Kubernetes deployments with advanced features

    Features:
    - Service Mesh integration (Istio/Linkerd)
    - Horizontal Pod Autoscaling (HPA)
    - Network Policies
    - Pod Security Policies
    - Resource Quotas
    """

    def __init__(self, config: KubernetesConfig):
        """Initialize Kubernetes enhancer"""
        self.config = config

    def generate_service_mesh_config(self) -> dict[str, Any]:
        """Generate Service Mesh configuration (Istio)"""
        if not self.config.enable_service_mesh:
            return {}

        return {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {"name": "nethical-recon", "namespace": self.config.namespace},
            "spec": {
                "hosts": ["nethical-recon.local"],
                "http": [
                    {
                        "match": [{"uri": {"prefix": "/api"}}],
                        "route": [{"destination": {"host": "nethical-recon-api", "port": {"number": 8000}}}],
                        "timeout": "30s",
                        "retries": {"attempts": 3, "perTryTimeout": "10s"},
                    }
                ],
            },
        }

    def generate_hpa_config(self) -> dict[str, Any]:
        """Generate Horizontal Pod Autoscaler configuration"""
        if not self.config.enable_hpa:
            return {}

        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {"name": "nethical-recon-hpa", "namespace": self.config.namespace},
            "spec": {
                "scaleTargetRef": {"apiVersion": "apps/v1", "kind": "Deployment", "name": "nethical-recon-worker"},
                "minReplicas": self.config.hpa_min_replicas,
                "maxReplicas": self.config.hpa_max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {"type": "Utilization", "averageUtilization": self.config.hpa_target_cpu},
                        },
                    },
                    {
                        "type": "Resource",
                        "resource": {"name": "memory", "target": {"type": "Utilization", "averageUtilization": 80}},
                    },
                ],
                "behavior": {
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [{"type": "Percent", "value": 50, "periodSeconds": 60}],
                    },
                    "scaleUp": {
                        "stabilizationWindowSeconds": 60,
                        "policies": [{"type": "Percent", "value": 100, "periodSeconds": 30}],
                    },
                },
            },
        }

    def generate_network_policy(self) -> dict[str, Any]:
        """Generate Network Policy for security"""
        if not self.config.enable_network_policies:
            return {}

        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "nethical-recon-netpol", "namespace": self.config.namespace},
            "spec": {
                "podSelector": {"matchLabels": {"app": "nethical-recon"}},
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [{"podSelector": {"matchLabels": {"app": "nethical-recon-api"}}}],
                        "ports": [{"protocol": "TCP", "port": 8000}],
                    }
                ],
                "egress": [
                    {
                        "to": [{"podSelector": {"matchLabels": {"app": "postgresql"}}}],
                        "ports": [{"protocol": "TCP", "port": 5432}],
                    },
                    {
                        "to": [{"podSelector": {"matchLabels": {"app": "redis"}}}],
                        "ports": [{"protocol": "TCP", "port": 6379}],
                    },
                ],
            },
        }

    def generate_pod_security_policy(self) -> dict[str, Any]:
        """Generate Pod Security Policy"""
        if not self.config.enable_pod_security:
            return {}

        return {
            "apiVersion": "policy/v1beta1",
            "kind": "PodSecurityPolicy",
            "metadata": {"name": "nethical-recon-psp"},
            "spec": {
                "privileged": False,
                "allowPrivilegeEscalation": False,
                "requiredDropCapabilities": ["ALL"],
                "volumes": ["configMap", "emptyDir", "secret", "persistentVolumeClaim"],
                "hostNetwork": False,
                "hostIPC": False,
                "hostPID": False,
                "runAsUser": {"rule": "MustRunAsNonRoot"},
                "seLinux": {"rule": "RunAsAny"},
                "fsGroup": {"rule": "RunAsAny"},
                "readOnlyRootFilesystem": True,
            },
        }

    def export_all_configs(self) -> dict[str, dict[str, Any]]:
        """Export all Kubernetes configurations"""
        return {
            "service_mesh": self.generate_service_mesh_config(),
            "hpa": self.generate_hpa_config(),
            "network_policy": self.generate_network_policy(),
            "pod_security_policy": self.generate_pod_security_policy(),
        }
