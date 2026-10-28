import pytest

from tests.helpers import BOUNDARY_OK, VALID, payload_with


def test_valid_submission_is_created(client):
    r = client.post("/vitals", json=VALID)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1
    assert body["patient_id"] == "P-1001"
    assert body["blood_pressure"] == {"systolic": 120, "diastolic": 80}
    assert body["glucose_level"] == 95.5
    assert "recorded_at" in body


def test_ids_count_up(client):
    assert client.post("/vitals", json=VALID).json()["id"] == 1
    assert client.post("/vitals", json=VALID).json()["id"] == 2


def test_whole_number_glucose_is_fine(client):
    assert client.post("/vitals", json=payload_with("glucose_level", 95)).status_code == 201


def test_patient_id_is_trimmed(client):
    r = client.post("/vitals", json=payload_with("patient_id", "  P-9  "))
    assert r.json()["patient_id"] == "P-9"


def test_extra_fields_are_ignored(client):
    r = client.post("/vitals", json={**VALID, "nickname": "x"})
    assert r.status_code == 201
    assert "nickname" not in r.json()


@pytest.mark.parametrize("path,value", BOUNDARY_OK)
def test_values_on_the_limits_are_accepted(client, path, value):
    assert client.post("/vitals", json=payload_with(path, value)).status_code == 201


def test_saved_record_can_be_read_back(client):
    client.post("/vitals", json=VALID)
    r = client.get("/patients/P-1001/vitals")
    assert r.status_code == 200
    assert len(r.json()) == 1
