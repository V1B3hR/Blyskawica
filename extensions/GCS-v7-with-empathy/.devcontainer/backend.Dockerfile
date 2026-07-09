# Use an official Python image with Node.js for frontend tooling
FROM python:3.10-slim-bullseye

# Install Node.js and npm
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Set the working directory
WORKDIR /workspace

# Copy requirements file
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
