def post(client, patient_id, systolic, diastolic, glucose):
    client.post("/vitals", json={
        "patient_id": patient_id,
        "age": 40,
        "blood_pressure": {"systolic": systolic, "diastolic": diastolic},
        "glucose_level": glucose,
    })


def test_summary_has_averages_and_count(client):
    post(client, "P-1", 120, 80, 90)
    post(client, "P-1", 130, 90, 100)
    post(client, "P-1", 140, 100, 110)
    r = client.get("/patients/P-1/summary")
    assert r.status_code == 200
    assert r.json() == {
        "patient_id": "P-1",
        "record_count": 3,
        "averages": {"systolic": 130.0, "diastolic": 90.0, "glucose": 100.0},
    }


def test_summary_ignores_other_patients(client):
    post(client, "P-1", 120, 80, 90)
    post(client, "P-2", 200, 150, 300)
    body = client.get("/patients/P-1/summary").json()
    assert body["record_count"] == 1
    assert body["averages"]["systolic"] == 120


def test_summary_rounds_to_two_decimals(client):
    post(client, "P-1", 100, 60, 90)
    post(client, "P-1", 100, 60, 90)
    post(client, "P-1", 101, 61, 91)
    assert client.get("/patients/P-1/summary").json()["averages"]["systolic"] == 100.33


def test_summary_for_unknown_patient_is_404(client):
    r = client.get("/patients/nobody/summary")
    assert r.status_code == 404
    assert "nobody" in r.json()["detail"]
