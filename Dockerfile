# 1. Use an official lightweight Python image
FROM python:3.11-slim

# 2. Set environment variables to optimize Python inside the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install system dependencies required for PostgreSQL (psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the project files into the container
COPY . /app/

# 7. Expose the port Django will run on
EXPOSE 8000

# 8. Command to run the application using local settings
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]