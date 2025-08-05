# 1. Use an official Python runtime as a parent image
# Using a slim version to keep the image size smaller
FROM python:3.11-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Install system dependencies
#    - 'build-essential' is needed for some Python packages that compile from source.
#    - 'ffmpeg' is a runtime dependency for markitdown's audio processing.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy the dependencies file and install them
#    Using --no-cache-dir reduces the image size
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application's code into the container
COPY . .

# 6. Set the entrypoint for the container
#    Gunicorn is a production-ready web server for Python.
#    - '0.0.0.0' makes the server accessible from outside the container.
#    - '$PORT' is the environment variable Cloud Run uses to provide the port.
#    - 'main:app' points to the Flask 'app' object in the 'main.py' file.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 main:app
