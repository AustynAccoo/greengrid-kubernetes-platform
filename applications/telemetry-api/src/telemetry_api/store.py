"""Bounded in-memory storage for recent telemetry."""

from collections import deque
from threading import Lock

from telemetry_api.models import TelemetryRecord


class TelemetryStore:
    """Thread-safe bounded store that discards the oldest record first."""

    def __init__(self, retention_limit: int = 1_000) -> None:
        if retention_limit < 1:
            raise ValueError("retention_limit must be at least 1")
        self._records: deque[TelemetryRecord] = deque(maxlen=retention_limit)
        self._lock = Lock()

    @property
    def retention_limit(self) -> int:
        return self._records.maxlen or 0

    def add(self, record: TelemetryRecord) -> int:
        """Store a reading and return the retained count."""

        with self._lock:
            self._records.append(record)
            return len(self._records)

    def list_records(self) -> list[TelemetryRecord]:
        """Return a stable snapshot in ingestion order."""

        with self._lock:
            return list(self._records)

    def __len__(self) -> int:
        with self._lock:
            return len(self._records)
