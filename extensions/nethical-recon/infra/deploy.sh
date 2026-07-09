#!/bin/bash
# Quick deployment script for Nethical Recon on Kubernetes

set -e

NAMESPACE="${NAMESPACE:-nethical-recon}"
HELM_RELEASE="${HELM_RELEASE:-nethical}"
DEPLOYMENT_MODE="${DEPLOYMENT_MODE:-helm}"  # helm or kubectl

echo "🚀 Deploying Nethical Recon to Kubernetes"
echo "   Mode: $DEPLOYMENT_MODE"
echo "   Namespace: $NAMESPACE"
echo "   Release: $HELM_RELEASE"
echo ""

# Check prerequisites
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl."
    exit 1
fi

if [ "$DEPLOYMENT_MODE" = "helm" ]; then
    if ! command -v helm &> /dev/null; then
        echo "❌ helm not found. Please install helm."
        exit 1
    fi
fi

# Function to check if namespace exists
namespace_exists() {
    kubectl get namespace "$1" &> /dev/null
}

# Deploy using Helm
deploy_helm() {
    echo "📦 Deploying with Helm..."
    
    # Check if release exists
    if helm list -n "$NAMESPACE" | grep -q "$HELM_RELEASE"; then
        echo "⬆️  Upgrading existing release..."
        helm upgrade "$HELM_RELEASE" infra/helm/nethical-recon \
            --namespace "$NAMESPACE" \
            --create-namespace \
            --wait \
            --timeout 10m
    else
        echo "📥 Installing new release..."
        helm install "$HELM_RELEASE" infra/helm/nethical-recon \
            --namespace "$NAMESPACE" \
            --create-namespace \
            --wait \
            --timeout 10m
    fi
    
    echo ""
    echo "✅ Helm deployment complete!"
    echo ""
    helm status "$HELM_RELEASE" -n "$NAMESPACE"
}

# Deploy using kubectl
deploy_kubectl() {
    echo "📦 Deploying with kubectl..."
    
    # Create namespace if it doesn't exist
    if ! namespace_exists "$NAMESPACE"; then
        echo "Creating namespace: $NAMESPACE"
        kubectl apply -f infra/k8s/namespace.yaml
    fi
    
    # Apply resources in order
    echo "Applying ConfigMap and Secrets..."
    kubectl apply -f infra/k8s/configmap.yaml
    kubectl apply -f infra/k8s/secrets.yaml
    
    echo "Deploying PostgreSQL..."
    kubectl apply -f infra/k8s/postgres.yaml
    
    echo "Deploying Redis..."
    kubectl apply -f infra/k8s/redis.yaml
    
    echo "Waiting for databases to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=database -n "$NAMESPACE" --timeout=300s || true
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=cache -n "$NAMESPACE" --timeout=300s || true
    
    echo "Creating PersistentVolumeClaim..."
    kubectl apply -f infra/k8s/pvc.yaml
    
    echo "Deploying application services..."
    kubectl apply -f infra/k8s/api.yaml
    kubectl apply -f infra/k8s/worker.yaml
    kubectl apply -f infra/k8s/scheduler.yaml
    
    echo "Waiting for application services to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=api -n "$NAMESPACE" --timeout=300s || true
    
    echo ""
    echo "✅ kubectl deployment complete!"
}

# Main deployment
if [ "$DEPLOYMENT_MODE" = "helm" ]; then
    deploy_helm
else
    deploy_kubectl
fi

echo ""
echo "📊 Checking deployment status..."
kubectl get pods -n "$NAMESPACE"

echo ""
echo "🎉 Deployment finished!"
echo ""
echo "To access the API, run:"
echo "  kubectl port-forward -n $NAMESPACE svc/nethical-api 8000:8000"
echo ""
echo "Then visit:"
echo "  - API docs: http://localhost:8000/api/v1/docs"
echo "  - Health: http://localhost:8000/health"
echo "  - Metrics: http://localhost:8000/metrics"
echo ""
echo "To view logs:"
echo "  kubectl logs -n $NAMESPACE -l app.kubernetes.io/component=api -f"
echo ""
