# Use Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 80
EXPOSE 80

# Environment variable to change Flask's default port to 80
ENV FLASK_RUN_PORT=80

# Run the application
CMD ["python", "run.py"] 