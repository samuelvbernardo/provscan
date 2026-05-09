#!/bin/sh

set -e

RUN_MIGRATIONS="${RUN_MIGRATIONS:-true}"
RUN_COLLECTSTATIC="${RUN_COLLECTSTATIC:-true}"
RUN_CREATE_CACHE_TABLE="${RUN_CREATE_CACHE_TABLE:-false}"
RUN_DEPLOY_CHECKS="${RUN_DEPLOY_CHECKS:-false}"
GUNICORN_WORKERS="${GUNICORN_WORKERS:-${WEB_CONCURRENCY:-3}}"
GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"
GUNICORN_BIND="${GUNICORN_BIND:-0.0.0.0:${PORT:-8000}}"

if [ "$RUN_DEPLOY_CHECKS" = "true" ]; then
    echo "Executando checks de deploy..."
    python manage.py check --deploy
fi

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Aplicando migrations..."
    python manage.py migrate --noinput
fi

if [ "$RUN_CREATE_CACHE_TABLE" = "true" ]; then
    echo "Criando tabela de cache de banco, se configurada..."
    python manage.py createcachetable
fi

if [ "$RUN_COLLECTSTATIC" = "true" ]; then
    echo "Coletando arquivos estaticos..."
    python manage.py collectstatic --noinput
fi

echo "Iniciando servidor..."
exec gunicorn scan_api.wsgi:application \
    --bind "$GUNICORN_BIND" \
    --workers "$GUNICORN_WORKERS" \
    --timeout "$GUNICORN_TIMEOUT" \
    --access-logfile - \
    --error-logfile -
