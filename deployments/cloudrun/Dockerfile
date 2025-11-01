# Cloud Run Deployment for P2P Dashboard
# Lightweight container serving the dashboard with real-time GitHub API integration

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    flask==3.0.0 \
    gunicorn==21.2.0 \
    PyGithub==2.1.1 \
    python-dotenv==1.0.0

# Copy application files
COPY dashboard/ /app/dashboard/
COPY src/ /app/src/
COPY server.py /app/

# Expose port for Cloud Run
ENV PORT=8080

# Run with gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 server:app
