FROM python:3.14-slim

WORKDIR /app

# Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN apt-get update
RUN apt-get install -y iputils-ping htop mc telnet

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
