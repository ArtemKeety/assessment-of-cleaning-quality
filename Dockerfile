FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y \
    coinor-cbc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pybabel compile -d locales -D messages

RUN ls -la locales/ru/LC_MESSAGES/messages.mo

COPY . .

