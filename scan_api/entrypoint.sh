#!/bin/sh

set -e

echo "Aplicando migrations..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor..."
gunicorn scan_api.wsgi:application --bind 0.0.0.0:8000 --timeout 120