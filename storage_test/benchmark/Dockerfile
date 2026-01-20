FROM python:3.13-slim

WORKDIR /benchmark

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /opt/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        time \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

ENTRYPOINT ["python"]
