# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies for Tesseract, OpenCV, and Poppler
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application code into the container
COPY . .

# Create uploads folder
RUN mkdir -p uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 10000

# Start the application using gunicorn
# Render expects the app to listen on the PORT environment variable
CMD gunicorn --bind 0.0.0.0:$PORT app:app
