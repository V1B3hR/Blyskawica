#!/usr/bin/env python3
"""
Remote Secure Training Usage Examples

This script demonstrates how to use the AiMedRes remote secure training system
in various scenarios including programmatic API usage and CLI examples.
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from remote_training_manager import RemoteTrainingManager
from security.auth import SecureAuthManager
from security.encryption import DataEncryption


def example_1_programmatic_training():
    """Example 1: Programmatic training workflow using Python API"""
    print("🔬 Example 1: Programmatic Training Workflow")
    print("=" * 60)

    # Initialize the secure training system
    auth_config = {'jwt_secret': 'example_secret'}
    auth_manager = SecureAuthManager(auth_config)
    encryption = DataEncryption()
    training_manager = RemoteTrainingManager(auth_manager, encryption)

    print("✅ Remote training system initialized")

    # Get API keys for demo
    admin_keys = [k for k, v in auth_manager.api_keys.items() if 'admin' in v['roles']]
    user_keys = [k for k, v in auth_manager.api_keys.items() if 'admin' not in v['roles']]

    admin_key = admin_keys[0] if admin_keys else None
    user_key = user_keys[0] if user_keys else None

    print("🔑 Generated API Keys:")
    print(f"   Admin: {admin_key[:25]}...")
    print(f"   User:  {user_key[:25]}...")

    # Submit multiple training jobs
    training_configs = [
        {
            'model_type': 'alzheimer_classifier',
            'dataset_source': 'synthetic_test_data',
            'description': 'Basic Alzheimer classifier'
        },
        {
            'model_type': 'adaptive_neural_net',
            'dataset_source': 'synthetic_test_data',
            'description': 'Adaptive neural network with biological cycles'
        }
    ]

    job_ids = []
    for i, config in enumerate(training_configs):
        print(f"\n📤 Submitting training job {i+1}: {config['description']}")

        try:
            job_id = training_manager.submit_training_job(f'user_{i+1}', config)
            job_ids.append((job_id, f'user_{i+1}'))
            print(f"   ✅ Job submitted: {job_id}")
        except Exception as e:
            print(f"   ❌ Failed to submit job: {e}")

    # Monitor training progress
    print(f"\n⏳ Monitoring {len(job_ids)} training jobs...")

    max_wait = 15  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait:
        completed_jobs = 0

        for job_id, user_id in job_ids:
            try:
                status = training_manager.get_job_status(job_id, user_id)
                job_status = status['status']
                progress = status['progress']

                print(f"   📊 Job {job_id[:8]}... - Status: {job_status} - Progress: {progress:.1%}")

                if job_status in ['completed', 'failed', 'cancelled']:
                    completed_jobs += 1

                    if job_status == 'completed':
                        results = status.get('results', {})
                        accuracy = results.get('training_accuracy', 'N/A')
                        duration = results.get('training_duration_seconds', 'N/A')
                        print(f"     ✅ Accuracy: {accuracy}, Duration: {duration}s")

            except Exception as e:
                print(f"   ❌ Error checking job {job_id[:8]}...: {e}")

        if completed_jobs == len(job_ids):
            break

        time.sleep(2)

    # Get system status
    print("\n📈 System Status:")
    try:
        sys_status = training_manager.get_system_status()
        print(f"   Active Jobs: {sys_status['active_jobs']}")
        print(f"   Completed Jobs: {sys_status['completed_jobs']}")
        print(f"   System Capacity: {sys_status['capacity_available']}/{sys_status['max_concurrent_jobs']}")
        print(f"   System Health: {'✅ Healthy' if sys_status['system_healthy'] else '❌ Unhealthy'}")
    except Exception as e:
        print(f"   ❌ Error getting system status: {e}")

    # Download trained models
    print("\n💾 Downloading trained models...")
    for job_id, user_id in job_ids:
        try:
            encrypted_model = training_manager.get_encrypted_model(job_id, user_id)
            if encrypted_model:
                # Decrypt model to verify
                decrypted_model = encryption.decrypt_data(encrypted_model)
                model_info = decrypted_model.get('model_params', {})

                print(f"   ✅ Model {job_id[:8]}... downloaded and decrypted successfully")
                print(f"      Model Type: {model_info.get('model_type', 'Unknown')}")
                print(f"      Feature Count: {len(model_info.get('feature_columns', []))}")
        except Exception as e:
            print(f"   ❌ Error downloading model {job_id[:8]}...: {e}")

    print("\n🎉 Example 1 completed successfully!")

def example_2_security_features():
    """Example 2: Security features demonstration"""
    print("\n🔐 Example 2: Security Features Demonstration")
    print("=" * 60)

    # Initialize components
    auth_manager = SecureAuthManager({'jwt_secret': 'security_demo'})
    encryption = DataEncryption()

    print("✅ Security components initialized")

    # Demonstrate API key validation
    print("\n🔑 API Key Security:")
    valid_keys = list(auth_manager.api_keys.keys())
    valid_key = valid_keys[0]

    # Test valid key
    is_valid, user_info = auth_manager.validate_api_key(valid_key)
    print(f"   Valid key test: {'✅ Passed' if is_valid else '❌ Failed'}")
    if user_info:
        print(f"   User: {user_info['user_id']}, Roles: {user_info['roles']}")

    # Test invalid key
    is_valid, user_info = auth_manager.validate_api_key('invalid_key_12345')
    print(f"   Invalid key test: {'✅ Rejected' if not is_valid else '❌ Accepted (BAD!)'}")

    # Demonstrate data encryption
    print("\n🔒 Data Encryption:")

    # Test symmetric encryption
    sensitive_data = {
        'patient_id': 'P12345',
        'medical_record': 'Confidential diagnosis information',
        'personal_info': 'SSN: 123-45-6789'
    }

    encrypted_data = encryption.encrypt_data(sensitive_data)
    decrypted_data = encryption.decrypt_data(encrypted_data)

    print(f"   Original data: {len(str(sensitive_data))} characters")
    print(f"   Encrypted data: {len(encrypted_data)} characters")
    print(f"   Decryption test: {'✅ Passed' if decrypted_data == sensitive_data else '❌ Failed'}")

    # Test medical data anonymization
    medical_data = {
        'patient_id': 'P67890',
        'name': 'John Doe',
        'birth_date': '1958-01-15',
        'ssn': '987-65-4321',
        'age': 65,
        'diagnosis': 'MCI',
        'mmse_score': 24
    }

    anonymized_data = encryption.anonymize_medical_data(medical_data)

    print("\n🎭 Medical Data Anonymization:")
    print(f"   Original identifiers removed: {'✅ Yes' if 'patient_id' not in anonymized_data else '❌ No'}")
    print(f"   Medical data preserved: {'✅ Yes' if anonymized_data.get('diagnosis') == 'MCI' else '❌ No'}")
    print(f"   Anonymization metadata added: {'✅ Yes' if anonymized_data.get('anonymized') else '❌ No'}")

    # Test role-based access
    print("\n👤 Role-Based Access Control:")

    admin_key = None
    user_key = None

    for key, info in auth_manager.api_keys.items():
        if 'admin' in info['roles']:
            admin_key = key
        elif 'admin' not in info['roles']:
            user_key = key

    if admin_key:
        _, admin_info = auth_manager.validate_api_key(admin_key)
        has_admin_role = auth_manager.has_role(admin_info, 'admin')
        has_user_role = auth_manager.has_role(admin_info, 'user')
        print(f"   Admin has admin role: {'✅ Yes' if has_admin_role else '❌ No'}")
        print(f"   Admin has user role: {'✅ Yes' if has_user_role else '❌ No'}")

    if user_key:
        _, user_info = auth_manager.validate_api_key(user_key)
        has_admin_role = auth_manager.has_role(user_info, 'admin')
        has_user_role = auth_manager.has_role(user_info, 'user')
        print(f"   User has admin role: {'❌ No' if not has_admin_role else '❌ Yes (BAD!)'}")
        print(f"   User has user role: {'✅ Yes' if has_user_role else '❌ No'}")

    print("\n🎉 Example 2 completed successfully!")

def example_3_cli_usage():
    """Example 3: Command-line usage examples"""
    print("\n💻 Example 3: Command-Line Usage Examples")
    print("=" * 60)

    print("🚀 Starting API server for CLI demonstration...")

    # Note: In a real scenario, you would start the server separately
    # This is just showing the commands you would use

    cli_examples = [
        {
            'description': 'Health Check',
            'command': 'curl -s http://localhost:5000/api/v1/health'
        },
        {
            'description': 'Get Training Examples',
            'command': 'curl -s http://localhost:5000/api/v1/training/examples'
        },
        {
            'description': 'Submit Training Job',
            'command': '''curl -X POST http://localhost:5000/api/v1/training/submit \\
  -H "X-API-Key: dmk_YOUR_API_KEY_HERE" \\
  -H "Content-Type: application/json" \\
  -d '{"model_type": "alzheimer_classifier", "dataset_source": "synthetic_test_data"}'```'''
        },
        {
            'description': 'Check Job Status',
            'command': 'curl -H "X-API-Key: dmk_YOUR_API_KEY_HERE" http://localhost:5000/api/v1/training/status/JOB_ID'
        },
        {
            'description': 'List User Jobs',
            'command': 'curl -H "X-API-Key: dmk_YOUR_API_KEY_HERE" http://localhost:5000/api/v1/training/jobs'
        },
        {
            'description': 'Download Trained Model',
            'command': 'curl -H "X-API-Key: dmk_YOUR_API_KEY_HERE" http://localhost:5000/api/v1/training/model/JOB_ID'
        },
        {
            'description': 'System Status (Admin)',
            'command': 'curl -H "X-API-Key: dmk_ADMIN_KEY_HERE" http://localhost:5000/api/v1/admin/training/status'
        }
    ]

    for i, example in enumerate(cli_examples, 1):
        print(f"\n📋 CLI Example {i}: {example['description']}")
        print("   Command:")
        print(f"   {example['command']}")

    print("\n💡 Complete CLI Workflow:")
    workflow = """
# 1. Start the API server
python3 secure_api_server.py --port 5000

# 2. Health check
curl -s http://localhost:5000/api/v1/health | jq .

# 3. Submit training job
JOB_ID=$(curl -s -X POST http://localhost:5000/api/v1/training/submit \\
  -H "X-API-Key: $USER_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"model_type": "alzheimer_classifier", "dataset_source": "synthetic_test_data"}' | \\
  jq -r .job_id)

# 4. Monitor progress
while true; do
  STATUS=$(curl -s -H "X-API-Key: $USER_API_KEY" \\
    http://localhost:5000/api/v1/training/status/$JOB_ID | jq -r .status)
  echo "Job status: $STATUS"
  if [[ "$STATUS" == "completed" || "$STATUS" == "failed" ]]; then
    break
  fi
  sleep 2
done

# 5. Download model
curl -H "X-API-Key: $USER_API_KEY" \\
  http://localhost:5000/api/v1/training/model/$JOB_ID > trained_model.json
"""

    print(workflow)
    print("\n🎉 Example 3 completed successfully!")

def example_4_production_deployment():
    """Example 4: Production deployment considerations"""
    print("\n🏭 Example 4: Production Deployment Considerations")
    print("=" * 60)

    print("🔧 Environment Setup:")
    env_vars = [
        'export DUETMIND_MASTER_KEY="your-secure-master-key-256-bits"',
        'export FLASK_SECRET_KEY="your-flask-secret-key-here"',
        'export JWT_SECRET="your-jwt-secret-key-here"',
        'export MAX_FAILED_ATTEMPTS="5"',
        'export LOCKOUT_DURATION_MINUTES="15"',
        'export TOKEN_EXPIRY_HOURS="24"'
    ]

    for var in env_vars:
        print(f"   {var}")

    print("\n🔒 SSL/HTTPS Setup:")
    ssl_commands = [
        '# Generate SSL certificate (production should use CA-signed)',
        'openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes',
        '',
        '# Start server with SSL',
        'python3 secure_api_server.py --ssl-cert cert.pem --ssl-key key.pem --port 443'
    ]

    for cmd in ssl_commands:
        print(f"   {cmd}")

    print("\n🐳 Docker Deployment:")
    dockerfile = '''# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python3", "secure_api_server.py", "--host", "0.0.0.0"]'''

    print(dockerfile)

    print("\n☸️ Kubernetes Deployment:")
    k8s_config = '''# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aimedres-training-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aimedres-training-api
  template:
    metadata:
      labels:
        app: aimedres-training-api
    spec:
      containers:
      - name: api
        image: aimedres/training-api:latest
        ports:
        - containerPort: 5000
        env:
        - name: DUETMIND_MASTER_KEY
          valueFrom:
            secretKeyRef:
              name: aimedres-secrets
              key: master-key'''

    print(k8s_config)

    print("\n📊 Monitoring Setup:")
    monitoring_tips = [
        '• Set up health check monitoring on /api/v1/health',
        '• Monitor API response times and error rates',
        '• Track training job success/failure rates',
        '• Set up alerts for system capacity limits',
        '• Log all security events and failed authentications',
        '• Monitor resource usage (CPU, memory, disk)',
        '• Set up backup procedures for training jobs and models'
    ]

    for tip in monitoring_tips:
        print(f"   {tip}")

    print("\n🎉 Example 4 completed successfully!")

def main():
    """Run all usage examples"""
    print("🧠 AiMedRes Remote Secure Training - Usage Examples")
    print("=" * 80)
    print("This script demonstrates various ways to use the remote training system.")
    print("All examples run locally without requiring a running API server.")
    print()

    try:
        example_1_programmatic_training()
        example_2_security_features()
        example_3_cli_usage()
        example_4_production_deployment()

        print("\n" + "=" * 80)
        print("🎊 All examples completed successfully!")
        print("\n💡 Next Steps:")
        print("   1. Start the API server: python3 secure_api_server.py")
        print("   2. Try the CLI examples with a running server")
        print("   3. Integrate the Python API into your applications")
        print("   4. Deploy to production with proper SSL and monitoring")
        print("   5. Read REMOTE_TRAINING_DOCUMENTATION.md for detailed info")

    except Exception as e:
        print(f"\n❌ Example failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
