# Use the official Python image as a base
FROM python:3.11-slim

# Set environment variables to prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /codecrafting

# Install system dependencies for ODBC and SQL Server driver
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
    # Add Microsoft package repository manually for Debian 10 (buster)
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file to install Python dependencies
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Copy the SSL certificate and key into the container
COPY ssl/cert.pem /etc/ssl/cert.pem
COPY ssl/key.pem /etc/ssl/key.pem

# Expose the HTTPS port
EXPOSE 443

# Start the app using Gunicorn with HTTPS support
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:443", "--certfile=/etc/ssl/cert.pem", "--keyfile=/etc/ssl/key.pem", "app:app"]
