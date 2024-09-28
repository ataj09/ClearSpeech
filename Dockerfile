FROM python:3.11.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

CMD ["rm -r /app"]

WORKDIR /app

RUN python -m venv /app/venv

COPY . .

RUN /app/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

CMD ["/app/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 
