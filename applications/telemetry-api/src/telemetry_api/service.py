"""Telemetry business logic independent of HTTP routing."""

import time
from threading import Lock

from telemetry_api.models import LoadResponse, TelemetryRecord
from telemetry_api.store import TelemetryStore


class TelemetryService:
    """Coordinate ingestion, retrieval, counters, and bounded load simulation."""

    def __init__(self, store: TelemetryStore) -> None:
        self.store = store
        self.submissions_total = 0
        self._counter_lock = Lock()

    def submit(self, record: TelemetryRecord) -> int:
        retained = self.store.add(record)
        with self._counter_lock:
            self.submissions_total += 1
        return retained

    def submission_count(self) -> int:
        """Return a thread-safe snapshot of the accepted-record counter."""

        with self._counter_lock:
            return self.submissions_total

    def retrieve(self) -> list[TelemetryRecord]:
        return self.store.list_records()

    @staticmethod
    def simulate_load(duration_ms: int) -> LoadResponse:
        """Perform bounded CPU work for local troubleshooting demonstrations."""

        deadline = time.perf_counter() + (duration_ms / 1_000)
        iterations = 0
        accumulator = 1
        while time.perf_counter() < deadline:
            accumulator = (accumulator * 31 + iterations) % 1_000_003
            iterations += 1
        del accumulator
        return LoadResponse(
            message="load simulation completed",
            duration_ms=duration_ms,
            iterations=iterations,
        )
