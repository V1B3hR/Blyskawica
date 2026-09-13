# Use ROCm-enabled PyTorch image as base for AMD compatibility
FROM rocm/pytorch:rocm6.0_ubuntu22.04_py3.10_pytorch2.1.2

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libsndfile1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user and set permissions
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "scripts/train_cognitive_industry.py"]