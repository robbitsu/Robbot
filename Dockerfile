# Use official Python image
FROM python:3

# Set work directory
WORKDIR /app

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
