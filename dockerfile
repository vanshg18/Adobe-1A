# Use Python 3.11.9 as base image
FROM --platform=linux/amd64 python:3.11.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from the root into the container
COPY . .

# Default command to run your script
CMD ["python", "main.py"]
