import logging

from tests.helpers import VALID


def messages(caplog):
    return [record.getMessage() for record in caplog.records if record.name.startswith("app")]


def test_saving_a_record_is_logged_at_info(client, caplog):
    with caplog.at_level(logging.INFO, logger="app"):
        client.post("/vitals", json=VALID)
    assert "Saved vitals record id=1" in messages(caplog)


def test_patient_id_is_only_logged_at_debug(client, caplog):
    with caplog.at_level(logging.INFO, logger="app"):
        client.post("/vitals", json=VALID)
    assert not any(VALID["patient_id"] in text for text in messages(caplog))

    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="app"):
        client.post("/vitals", json=VALID)
    assert any(VALID["patient_id"] in text for text in messages(caplog))


def test_rejected_request_is_logged_as_a_warning(client, caplog):
    with caplog.at_level(logging.WARNING, logger="app"):
        client.post("/vitals", json={**VALID, "age": 150})
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    assert "Rejected POST /vitals" in warnings[0].getMessage()


def test_unknown_patient_summary_is_logged_as_a_warning(client, caplog):
    with caplog.at_level(logging.WARNING, logger="app"):
        client.get("/patients/nobody/summary")
    assert any("nobody" in text for text in messages(caplog))


def test_warning_level_hides_the_info_messages(client, caplog):
    with caplog.at_level(logging.WARNING, logger="app"):
        client.post("/vitals", json=VALID)
    assert messages(caplog) == []
