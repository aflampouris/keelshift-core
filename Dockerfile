FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Minimal deps for now (we’ll pin later)
RUN pip install --upgrade pip \
 && pip install \
    "django>=5.0" \
    psycopg[binary] \
    redis \
    rq \
    reportlab \ 
    minio \
    pandas
COPY . /app
