FROM python:3.11-slim

# Install requirements for Cloud Run gateway
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the gateway app
COPY cloudrun-app.py /app/app.py
WORKDIR /app

EXPOSE 8080

CMD ["python", "app.py"]