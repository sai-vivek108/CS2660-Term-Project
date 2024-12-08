# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the app code into the container
COPY . .

# Expose the port Flask runs on
EXPOSE 8080

# Define the entry point
CMD ["python", "main.py"]
