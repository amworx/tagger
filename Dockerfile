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

# Create instance directory for SQLite database
RUN mkdir -p instance

# Initialize the database and create superadmin user
RUN python init_db.py

# Expose port 80
EXPOSE 80

# Environment variables for Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"] 