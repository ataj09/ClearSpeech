# app/Dockerfile

# Use the official Python image from DockerHub
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt
COPY ../requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code to the container
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]