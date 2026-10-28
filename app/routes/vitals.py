import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models import SummaryOut, VitalsIn, VitalsOut
from app.storage import store
from app.summary import summarize

logger = logging.getLogger(__name__)

router = APIRouter(tags=["vitals"])


@router.post("/vitals", response_model=VitalsOut, status_code=201, summary="Record vitals for a patient")
def add_vitals(data: VitalsIn):
    record = store.add(data)
    logger.info("Saved vitals record id=%s", record.id)
    logger.debug("Record id=%s belongs to patient %s", record.id, record.patient_id)
    return record


@router.get("/patients/{patient_id}/vitals", response_model=list[VitalsOut], summary="List a patient's vitals, newest first")
def patient_vitals(
    patient_id: str,
    limit: Optional[int] = Query(None, ge=1, description="Return at most this many records (the newest ones)"),
):
    records = store.for_patient(patient_id, limit)
    logger.debug("Returning %d record(s) for patient %s", len(records), patient_id)
    return records


@router.get("/patients/{patient_id}/summary", response_model=SummaryOut, summary="Average vitals and record count")
def patient_summary(patient_id: str):
    records = store.for_patient(patient_id)
    if not records:
        logger.warning("Summary asked for unknown patient %s", patient_id)
        raise HTTPException(status_code=404, detail=f"No vitals found for patient {patient_id}")
    return summarize(patient_id, records)
