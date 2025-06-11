FROM python:3.12-alpine
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt /app/

# Installa i pacchetti di sviluppo necessari per mysqlclient
RUN pip3 install --no-cache-dir  --no-compile -r requirements.txt
    
COPY . /app

ENTRYPOINT [ "python3", "/app/main.py" ]
##