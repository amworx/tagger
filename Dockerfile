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
RUN python -c "from app import db, create_app; \
    app = create_app(); \
    app.app_context().push(); \
    db.create_all(); \
    from app.models import User, UserRole; \
    if not User.query.filter_by(username='superadmin').first(): \
        from werkzeug.security import generate_password_hash; \
        user = User(username='superadmin', \
                   email='superadmin@example.com', \
                   password_hash=generate_password_hash('superadmin'), \
                   role=UserRole.SUPERADMIN); \
        db.session.add(user); \
        db.session.commit()"

# Expose port 80
EXPOSE 80

# Environment variables for Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"] 