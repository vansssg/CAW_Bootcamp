FROM python:3.12-slim AS builder

WORKDIR /install

COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

RUN groupadd -r appgroup && useradd -r -g appgroup -s /bin/false appuser
USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.getenv(\"PORT\",\"3000\")}/live', timeout=3)" || exit 1

# Migrations are a one-off job (`alembic upgrade head`), not this CMD.
# A down DATABASE_URL must not block the HTTP listener.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-3000} --timeout-keep-alive 5 --timeout-graceful-shutdown 30"]
