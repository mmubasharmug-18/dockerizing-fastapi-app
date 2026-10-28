import pytest

from tests.helpers import payload_with


def add_ages(client, patient_id, ages):
    for age in ages:
        data = payload_with("age", age)
        data["patient_id"] = patient_id
        client.post("/vitals", json=data)


def test_returns_all_records_for_the_patient_newest_first(client):
    add_ages(client, "P-1", [30, 31, 32])
    r = client.get("/patients/P-1/vitals")
    assert r.status_code == 200
    assert [v["age"] for v in r.json()] == [32, 31, 30]


def test_limit_returns_the_newest_records(client):
    add_ages(client, "P-1", [30, 31, 32])
    r = client.get("/patients/P-1/vitals", params={"limit": 2})
    assert [v["age"] for v in r.json()] == [32, 31]


def test_limit_larger_than_the_data(client):
    add_ages(client, "P-1", [30])
    assert len(client.get("/patients/P-1/vitals", params={"limit": 50}).json()) == 1


def test_other_patients_are_not_mixed_in(client):
    add_ages(client, "P-1", [30, 31])
    add_ages(client, "P-2", [50])
    assert len(client.get("/patients/P-1/vitals").json()) == 2
    assert len(client.get("/patients/P-2/vitals").json()) == 1


def test_unknown_patient_gives_an_empty_list(client):
    r = client.get("/patients/nobody/vitals")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.parametrize("limit", ["0", "-1", "abc", "1.5"])
def test_bad_limit_gives_400(client, limit):
    r = client.get("/patients/P-1/vitals", params={"limit": limit})
    assert r.status_code == 400
    assert r.json()["detail"][0]["field"] == "limit"
