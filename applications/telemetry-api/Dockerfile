FROM python:3.14.7-slim-bookworm@sha256:9ab8d9c8514b44f90cf0029dd42fdd7e9e211e639c8b995304cc04568dee900f

ARG APP_VERSION=0.1.0

LABEL org.opencontainers.image.title="GreenGrid Telemetry API" \
      org.opencontainers.image.description="Local API for fictional GreenGrid energy telemetry" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.source="https://github.com/AustynAccoo/greengrid-kubernetes-platform" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH="/app/src" \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

RUN groupadd --gid 10001 greengrid \
    && useradd --uid 10001 --gid greengrid --no-create-home --shell /usr/sbin/nologin greengrid \
    && python -m venv /opt/venv

COPY requirements.txt ./requirements.txt
RUN pip install --no-compile --requirement requirements.txt \
    && rm requirements.txt

COPY --chown=10001:10001 src/ ./src/

USER 10001:10001

EXPOSE 8000
STOPSIGNAL SIGTERM

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=2).read()"]

ENTRYPOINT ["uvicorn"]
CMD ["telemetry_api.main:app", "--app-dir", "/app/src", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
