FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir faker

COPY generate.py .

CMD ["python", "generate.py"]
