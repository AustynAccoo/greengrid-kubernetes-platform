"""Long-running telemetry generation process with graceful shutdown."""

import logging
import signal
import threading

from telemetry_generator import __version__
from telemetry_generator.client import TelemetryClient
from telemetry_generator.config import GeneratorConfig
from telemetry_generator.logging_config import configure_logging
from telemetry_generator.payloads import create_payload

LOGGER = logging.getLogger(__name__)


def run() -> None:
    """Generate and deliver telemetry until SIGINT or SIGTERM."""

    configure_logging()
    config = GeneratorConfig.from_environment()
    stop_event = threading.Event()

    def request_shutdown(signum: int, _frame: object) -> None:
        LOGGER.info("shutdown signal received", extra={"signal": signum})
        stop_event.set()

    signal.signal(signal.SIGINT, request_shutdown)
    signal.signal(signal.SIGTERM, request_shutdown)
    LOGGER.info("telemetry generator started", extra={"version": __version__})

    with TelemetryClient(config) as client:
        while not stop_event.is_set():
            delivered = client.send(create_payload())
            if delivered and config.health_file is not None:
                config.health_file.touch()
            stop_event.wait(config.interval_seconds)

    LOGGER.info("telemetry generator stopped")


if __name__ == "__main__":
    run()
