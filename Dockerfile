# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies (for Pillow, opencv, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libgl1-mesa-glx \
        libglib2.0-0 \
        && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure secret.py exists (user must provide it)
RUN test -f secret.py || (echo 'ERROR: secret.py not found. Please provide your Discord bot token in secret.py.' && exit 1)

# Expose no ports (Discord bots are outbound only)

# Run the bot
CMD ["python", "bot.py"]
