import pytest

from tests.helpers import MISSING, OUT_OF_RANGE, VALID, WRONG_TYPES, payload_with, payload_without


def assert_rejected(client, response, field):
    assert response.status_code == 400
    details = response.json()["detail"]
    assert details[0]["field"] == field
    assert field.split(".")[-1] in details[0]["message"]
    assert client.get("/patients/P-1001/vitals").json() == []


@pytest.mark.parametrize("path,value", OUT_OF_RANGE)
def test_out_of_range_gives_400(client, path, value):
    response = client.post("/vitals", json=payload_with(path, value))
    assert_rejected(client, response, path)


@pytest.mark.parametrize("path,value", WRONG_TYPES)
def test_wrong_data_type_gives_400(client, path, value):
    response = client.post("/vitals", json=payload_with(path, value))
    assert_rejected(client, response, path)


@pytest.mark.parametrize("path", MISSING)
def test_missing_field_gives_400(client, path):
    response = client.post("/vitals", json=payload_without(path))
    assert response.status_code == 400
    assert response.json()["detail"][0]["field"] == path
    assert "missing" in response.json()["detail"][0]["message"]


def test_message_names_the_rule_and_the_value(client):
    r = client.post("/vitals", json=payload_with("age", 150))
    assert r.json()["detail"][0]["message"] == "age must be an integer between 0 and 120 (got 150)"


def test_all_problems_are_listed_together(client):
    bad = {"patient_id": "", "age": 999, "blood_pressure": {"systolic": 1, "diastolic": 999}, "glucose_level": -1}
    r = client.post("/vitals", json=bad)
    assert r.status_code == 400
    assert len(r.json()["detail"]) == 5


def test_invalid_json_gives_400(client):
    r = client.post("/vitals", content=b"{not json", headers={"Content-Type": "application/json"})
    assert r.status_code == 400
    assert r.json()["detail"][0]["field"] == "body"


def test_empty_body_gives_400(client):
    r = client.post("/vitals")
    assert r.status_code == 400
    assert r.json()["detail"][0]["message"] == "request body is required"


def test_json_list_instead_of_object_gives_400(client):
    r = client.post("/vitals", json=[VALID])
    assert r.status_code == 400
    assert r.json()["detail"][0]["message"] == "request body must be a JSON object"
