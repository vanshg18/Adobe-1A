# Use Python 3.11.9 as base image
FROM --platform=linux/amd64 python:3.11.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure input/output directories exist even if empty
RUN mkdir -p /app/input /app/output

# Copy all files (including input/output folders)
COPY . .

# Mark input/output as volumes so they can be mounted
VOLUME ["/app/input", "/app/output"]

# Default command
CMD ["python", "main.py"]
