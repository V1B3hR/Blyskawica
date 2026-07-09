"""
[Test Suite: AMD ROCm hipFFT & OpenShift Orchestration]
Validates the containerization manifests and high-frequency signal processing routines
implemented for industrial predictive maintenance deployment.
"""

import os
import unittest
import shutil
import yaml
from pathlib import Path
from scripts.enterprise_rocm_orchestration import run_rocm_hipfft_emulation, generate_openshift_manifests, DATA_DIR, OUTPUT_DIR

class TestEnterpriseROCmOrchestration(unittest.TestCase):

    def setUp(self):
        """Set up and backup existing manifests if any."""
        self.project_root = Path(r"c:\Projekty\Blyskawica_V8")
        self.dockerfile_path = self.project_root / "Dockerfile"
        self.deployment_path = Path(OUTPUT_DIR) / "deployment.yaml"

        self.dockerfile_backup = None
        self.deployment_backup = None

        if self.dockerfile_path.exists():
            with open(self.dockerfile_path, "r", encoding="utf-8") as f:
                self.dockerfile_backup = f.read()

        if self.deployment_path.exists():
            with open(self.deployment_path, "r", encoding="utf-8") as f:
                self.deployment_backup = f.read()

    def tearDown(self):
        """Restore backups and clean up generated test outputs."""
        if self.dockerfile_backup is not None:
            with open(self.dockerfile_path, "w", encoding="utf-8") as f:
                f.write(self.dockerfile_backup)
        elif self.dockerfile_path.exists():
            os.remove(self.dockerfile_path)

        if self.deployment_backup is not None:
            with open(self.deployment_path, "w", encoding="utf-8") as f:
                f.write(self.deployment_backup)
        elif self.deployment_path.exists():
            os.remove(self.deployment_path)

    def test_hipfft_vibration_analysis(self):
        """Verify that the hipFFT emulation loads signals and runs spectrum analysis successfully."""
        # Ensure the test data directory exists and contains the IMS data
        self.assertTrue(os.path.exists(DATA_DIR), f"Data directory not found: {DATA_DIR}")
        ims_file = os.path.join(DATA_DIR, "nasa_ims_bearing_signals.json")
        self.assertTrue(os.path.exists(ims_file), f"NASA IMS dataset not found: {ims_file}")

        # Run the hipFFT emulation
        try:
            run_rocm_hipfft_emulation()
        except Exception as e:
            self.fail(f"run_rocm_hipfft_emulation failed with exception: {e}")

    def test_manifest_generation(self):
        """Verify that the OpenShift and Dockerfile manifests are generated with correct enterprise structures."""
        # Run generation
        generate_openshift_manifests()

        # Validate Dockerfile exists and contains ROCm base image
        self.assertTrue(self.dockerfile_path.exists(), "Dockerfile was not generated.")
        with open(self.dockerfile_path, "r", encoding="utf-8") as f:
            docker_content = f.read()
        self.assertIn("rocm/pytorch", docker_content, "Dockerfile must use ROCm PyTorch base image.")
        self.assertIn("scripts/train_cognitive_industry.py", docker_content, "Dockerfile must configure correct start command.")

        # Validate Kubernetes Deployment YAML
        self.assertTrue(self.deployment_path.exists(), "OpenShift Deployment YAML was not generated.")
        with open(self.deployment_path, "r", encoding="utf-8") as f:
            deployment_data = yaml.safe_load(f)

        # Assert correct structures in YAML manifest
        self.assertEqual(deployment_data["apiVersion"], "apps/v1")
        self.assertEqual(deployment_data["kind"], "Deployment")
        self.assertEqual(deployment_data["metadata"]["name"], "blyskawica-pinn-engine")
        self.assertEqual(deployment_data["metadata"]["namespace"], "blyskawica-enterprise")

        # Assert AMD GPU resources are requested
        container = deployment_data["spec"]["template"]["spec"]["containers"][0]
        self.assertIn("amd.com/gpu", container["resources"]["limits"], "AMD Instinct GPU limits must be requested.")
        self.assertEqual(container["resources"]["limits"]["amd.com/gpu"], "1")

if __name__ == "__main__":
    unittest.main()
