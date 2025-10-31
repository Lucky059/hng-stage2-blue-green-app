# watcher/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy watcher script
COPY watcher.py .

# Run watcher script
CMD ["python", "watcher.py"]

