from datetime import datetime, timezone
from threading import Lock
from typing import Optional

from app.models import VitalsIn, VitalsOut


class VitalsStore:
    def __init__(self):
        self._records = {}
        self._next_id = 1
        self._lock = Lock()

    def add(self, data: VitalsIn) -> VitalsOut:
        with self._lock:
            record = VitalsOut(id=self._next_id, recorded_at=datetime.now(timezone.utc), **data.model_dump())
            self._records.setdefault(record.patient_id, []).append(record)
            self._next_id += 1
        return record

    def for_patient(self, patient_id: str, limit: Optional[int] = None) -> list[VitalsOut]:
        with self._lock:
            records = list(self._records.get(patient_id, []))
        records.reverse()
        if limit is not None:
            records = records[:limit]
        return records

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
            self._next_id = 1


store = VitalsStore()
