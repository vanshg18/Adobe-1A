# Use an official Python runtime as a parent image, specifying the platform
FROM --platform=linux/amd64 python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python scripts into the container
COPY main.py .
COPY extract_utils.py .

# Set the command to run when the container starts
CMD ["python", "main.py"]
