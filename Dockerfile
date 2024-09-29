# Dockerfile

# Use the official Python image from DockerHub
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt to the container
COPY requirements.txt .

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy the FastAPI app code into the container
COPY ./app /app

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
