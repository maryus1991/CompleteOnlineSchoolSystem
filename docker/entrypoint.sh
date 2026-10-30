#!/bin/sh
set -e

echo "==> [Entrypoint] Starting CompleteOnlineSchoolSystem (aroedu.ir)..."

if [ -n "$POSTGRES_HOST" ]; then
  PG_PORT="${POSTGRES_PORT:-5432}"
  echo "==> Waiting for PostgreSQL at ${POSTGRES_HOST}:${PG_PORT}..."
  until nc -z "$POSTGRES_HOST" "$PG_PORT"; do
    sleep 1
  done
  echo "==> PostgreSQL is reachable!"
fi

if [ -n "$REDIS_HOST" ]; then
  RD_PORT="${REDIS_PORT:-6379}"
  echo "==> Waiting for Redis at ${REDIS_HOST}:${RD_PORT}..."
  until nc -z "$REDIS_HOST" "$RD_PORT"; do
    sleep 1
  done
  echo "==> Redis is reachable!"
fi

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "==> Running database migrations..."
  python manage.py migrate --noinput
fi

if [ "${RUN_COLLECTSTATIC:-true}" = "true" ]; then
  echo "==> Collecting static files to ${DJANGO_STATIC_ROOT:-/app/staticfiles}..."
  python manage.py collectstatic --noinput
fi

echo "==> Launching application server: $*"
exec "$@"
