FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the Chromium browser
RUN playwright install chromium

# Copy the server code
COPY server.py .

# Expose the port Render uses
ENV PORT=8000
EXPOSE 8000

# Run with Uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]