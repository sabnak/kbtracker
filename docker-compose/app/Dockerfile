# Base stage: Common setup for both dev and prod
FROM python:3.14-slim AS base

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Install supervisor (needed for both)
RUN apt-get update && \
    apt-get install -y supervisor && \
    rm -rf /var/lib/apt/lists/*

# Setup supervisor
RUN mkdir -p /var/log/supervisor
COPY docker-compose/app/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Setup entrypoint
COPY docker-compose/app/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Dev stage: Adds development tools, relies on volume mounts for source code
FROM base AS dev

RUN apt-get update && \
    apt-get install -y iputils-ping htop mc telnet && \
    rm -rf /var/lib/apt/lists/*

COPY docker-compose/app/s /usr/local/bin/s
RUN chmod +x /usr/local/bin/s

# Prod stage: Copies application source code into image
FROM base AS prod

COPY src/ ./src/

# Final stage: Select dev or prod based on MODE build argument
ARG MODE=prod
FROM ${MODE} AS final

EXPOSE 80

CMD ["/entrypoint.sh"]
