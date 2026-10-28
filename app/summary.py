from app.models import Averages, SummaryOut, VitalsOut


def summarize(patient_id: str, records: list[VitalsOut]) -> SummaryOut:
    count = len(records)
    return SummaryOut(
        patient_id=patient_id,
        record_count=count,
        averages=Averages(
            systolic=round(sum(r.blood_pressure.systolic for r in records) / count, 2),
            diastolic=round(sum(r.blood_pressure.diastolic for r in records) / count, 2),
            glucose=round(sum(r.glucose_level for r in records) / count, 2),
        ),
    )
