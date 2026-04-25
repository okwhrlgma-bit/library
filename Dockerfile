FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      libzbar0 \
      && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[ui]"

EXPOSE 8000 8501

ENV KORMARC_HOST=0.0.0.0
ENV KORMARC_PORT=8000
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "kormarc_auto.server.app"]
