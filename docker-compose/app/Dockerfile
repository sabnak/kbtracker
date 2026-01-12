FROM python:3.14-slim

WORKDIR /app

# Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN apt-get update && \
    apt-get install -y iputils-ping htop mc telnet supervisor && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/log/supervisor
COPY docker-compose/app/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY docker-compose/app/s /usr/local/bin/s
RUN chmod +x /usr/local/bin/s

COPY docker-compose/app/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
