FROM python:3.12.14-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

ARG APP_VERSION=0.1.0

LABEL org.opencontainers.image.title="GreenGrid Telemetry Generator" \
      org.opencontainers.image.description="Fictional telemetry producer for local GreenGrid demonstrations" \
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

STOPSIGNAL SIGTERM

HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import os,time; path='/tmp/greengrid-generator-healthy'; assert time.time()-os.path.getmtime(path) < 30"]

ENTRYPOINT ["python"]
CMD ["-m", "telemetry_generator.main"]
