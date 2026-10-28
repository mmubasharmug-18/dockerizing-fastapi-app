import pytest

from app.models import VitalsIn
from app.storage import VitalsStore
from tests.helpers import VALID, payload_with


@pytest.fixture
def store():
    return VitalsStore()


def vitals(**changes):
    payload = dict(VALID)
    payload.update(changes)
    return VitalsIn.model_validate(payload)


def test_ids_count_up_from_one(store):
    assert store.add(vitals()).id == 1
    assert store.add(vitals()).id == 2


def test_record_has_a_utc_timestamp(store):
    record = store.add(vitals())
    assert record.recorded_at.utcoffset().total_seconds() == 0


def test_newest_record_comes_first(store):
    store.add(vitals(age=30))
    store.add(vitals(age=31))
    assert [r.age for r in store.for_patient("P-1001")] == [31, 30]


def test_limit_keeps_the_newest(store):
    for age in (30, 31, 32):
        store.add(vitals(age=age))
    assert [r.age for r in store.for_patient("P-1001", limit=2)] == [32, 31]


def test_limit_larger_than_data(store):
    store.add(vitals())
    assert len(store.for_patient("P-1001", limit=50)) == 1


def test_unknown_patient_gives_empty_list(store):
    assert store.for_patient("nobody") == []


def test_patients_are_kept_apart(store):
    store.add(vitals(patient_id="A"))
    store.add(vitals(patient_id="B"))
    assert len(store.for_patient("A")) == 1
    assert len(store.for_patient("B")) == 1


def test_clear_resets_everything(store):
    store.add(vitals())
    store.clear()
    assert store.for_patient("P-1001") == []
    assert store.add(vitals()).id == 1
