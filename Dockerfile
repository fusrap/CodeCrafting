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

# Expose the port the app runs on
EXPOSE 8000

# Start the app using Gunicorn with 4 worker processes
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
