from app.models import VitalsIn
from app.storage import VitalsStore
from app.summary import summarize


def record(store, systolic, diastolic, glucose):
    data = {"patient_id": "P-1", "age": 40,
            "blood_pressure": {"systolic": systolic, "diastolic": diastolic}, "glucose_level": glucose}
    return store.add(VitalsIn.model_validate(data))


def test_averages_and_count():
    store = VitalsStore()
    record(store, 120, 80, 90)
    record(store, 130, 90, 100)
    record(store, 140, 100, 110)
    summary = summarize("P-1", store.for_patient("P-1"))
    assert summary.record_count == 3
    assert summary.averages.systolic == 130
    assert summary.averages.diastolic == 90
    assert summary.averages.glucose == 100


def test_single_record():
    store = VitalsStore()
    record(store, 118, 76, 88.4)
    summary = summarize("P-1", store.for_patient("P-1"))
    assert summary.record_count == 1
    assert summary.averages.glucose == 88.4


def test_averages_are_rounded_to_two_decimals():
    store = VitalsStore()
    record(store, 100, 60, 90)
    record(store, 100, 60, 90)
    record(store, 101, 61, 91)
    averages = summarize("P-1", store.for_patient("P-1")).averages
    assert averages.systolic == 100.33
    assert averages.glucose == 90.33
