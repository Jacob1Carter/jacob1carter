FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Flask default port (change if needed)
EXPOSE 5000

# Run the app
CMD ["python", "main.py"]