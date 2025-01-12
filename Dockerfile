FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /codecrafting

RUN apt-get update && \
    apt-get install -y \
    curl \
    gnupg2 \
    unixodbc \
    unixodbc-dev \
    libodbc1 \
    odbcinst \
    odbcinst1debian2 \
    gcc \
    g++ \
    apt-transport-https && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY ssl/cert.pem /etc/ssl/cert.pem
COPY ssl/key.pem /etc/ssl/key.pem

EXPOSE 443

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:443", "--certfile=/etc/ssl/cert.pem", "--keyfile=/etc/ssl/key.pem", "app:app"]




