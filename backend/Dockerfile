# ── build stage ──
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt pyproject.toml ./
COPY src/ src/
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt \
    && PYTHONPATH=/install/lib/python3.12/site-packages pip install --no-cache-dir --prefix=/install .

# ── runtime stage ──
FROM python:3.12-slim

RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

WORKDIR /app

COPY --from=builder /install /usr/local
COPY src/ src/
COPY alembic.ini .

RUN chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "applytrack.main:app", "--host", "0.0.0.0", "--port", "8000"]
