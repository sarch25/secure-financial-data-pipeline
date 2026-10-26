FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py storage.py ./
RUN useradd --create-home appuser && mkdir -p /data && chown appuser:appuser /data
USER appuser
ENV DATABASE_PATH=/data/events.db BIND_HOST=0.0.0.0
EXPOSE 5000
CMD ["python", "app.py"]
