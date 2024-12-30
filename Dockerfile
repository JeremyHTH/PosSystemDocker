# Use Python 3.9 (or another version) as base
FROM python:3.9-slim

# Set a working directory inside the container
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ ./app

# Expose port 5000 for Flask
EXPOSE 5000

# Set environment variables so Python writes output directly
ENV PYTHONUNBUFFERED=1

# Run the Flask app
CMD ["python", "app/main.py"]
