# Use Node.js for frontend build
FROM node:18-alpine AS frontend-build

# Set working directory
WORKDIR /uptime-tracker

# Copy frontend source code
COPY frontend/ ./frontend
WORKDIR /uptime-tracker/frontend
RUN npm install && npm run build

# Use Python for runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /uptime-tracker

# Install system dependencies
RUN apt-get update && apt-get install -y \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/ ./backend

WORKDIR /uptime-tracker/backend

RUN pip install --no-cache-dir -r requirements.txt

COPY --from=frontend-build /uptime-tracker/frontend/dist ../frontend/dist

# Create external directory for config and database
RUN mkdir -p external

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Start the application
CMD ["python3", "app.py"] 