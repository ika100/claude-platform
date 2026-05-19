# syntax=docker/dockerfile:1.7

FROM python:{{ python_version }}-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project 2>/dev/null || uv sync --no-dev --no-install-project

COPY src ./src
COPY README.md ./
RUN uv sync --frozen --no-dev 2>/dev/null || uv sync --no-dev


FROM python:{{ python_version }}-slim AS runtime

RUN groupadd -r app && useradd -r -g app -d /app -s /usr/sbin/nologin app

WORKDIR /app

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/src /app/src

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT={{ port }}

USER app

EXPOSE {{ port }}

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, sys; urllib.request.urlopen('http://localhost:{{ port }}/health', timeout=3); sys.exit(0)" || exit 1

CMD ["uvicorn", "{{ module_name }}.main:app", "--host", "0.0.0.0", "--port", "{{ port }}"]
