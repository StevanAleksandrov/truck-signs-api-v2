#!/bin/sh
set -e

cd /app/src

echo "Waiting for PostgreSQL database..."

while ! python - <<'PY'
import os
import socket
import sys

host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))

try:
    with socket.create_connection((host, port), timeout=2):
        sys.exit(0)
except OSError:
    sys.exit(1)
PY
do
  echo "Database is not ready yet. Waiting..."
  sleep 2
done

echo "PostgreSQL is ready"

echo "Running database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating Django superuser if configured and not existing..."
python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.getenv("DJANGO_SUPERUSER_USERNAME")
email = os.getenv("DJANGO_SUPERUSER_EMAIL", "")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if username and password:
    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists. Skipping creation.")
    else:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created.")
else:
    print("Superuser environment variables are not fully set. Skipping creation.")
PY

echo "Starting Gunicorn WSGI application..."
exec gunicorn tsa_app.wsgi:application --bind 0.0.0.0:8000