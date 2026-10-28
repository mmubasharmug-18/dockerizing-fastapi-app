import pytest
from pydantic import ValidationError

from app.errors import field_name, format_errors, short
from app.models import VitalsIn
from tests.helpers import VALID, payload_with, payload_without


def api_errors(payload):
    with pytest.raises(ValidationError) as info:
        VitalsIn.model_validate(payload)
    return format_errors([{**e, "loc": ("body",) + e["loc"]} for e in info.value.errors()])


def test_out_of_range_message_states_the_rule_and_the_value():
    [error] = api_errors(payload_with("age", 150))
    assert error["field"] == "age"
    assert "age must be an integer between 0 and 120" in error["message"]
    assert "got 150" in error["message"]


def test_nested_field_uses_dotted_name():
    [error] = api_errors(payload_with("blood_pressure.systolic", 400))
    assert error["field"] == "blood_pressure.systolic"
    assert "between 50 and 300" in error["message"]


def test_missing_field_says_so():
    [error] = api_errors(payload_without("glucose_level"))
    assert error["message"].endswith("(field is missing)")


def test_empty_blood_pressure_reports_both_parts():
    errors = api_errors(payload_with("blood_pressure", {}))
    assert {e["field"] for e in errors} == {"blood_pressure.systolic", "blood_pressure.diastolic"}


def test_every_wrong_field_is_reported_at_once():
    payload = {"patient_id": "", "age": 999, "blood_pressure": {"systolic": 1, "diastolic": 999}, "glucose_level": -1}
    fields = {e["field"] for e in api_errors(payload)}
    assert fields == {"patient_id", "age", "blood_pressure.systolic", "blood_pressure.diastolic", "glucose_level"}


def test_invalid_json_body():
    errors = format_errors([{"type": "json_invalid", "loc": ("body", 5), "msg": "JSON decode error"}])
    assert errors == [{"field": "body", "message": "request body must be valid JSON"}]


def test_missing_body():
    errors = format_errors([{"type": "missing", "loc": ("body",), "msg": "Field required"}])
    assert errors[0]["message"] == "request body is required"


def test_body_that_is_not_an_object():
    errors = format_errors([{"type": "model_attributes_type", "loc": ("body",), "msg": "bad", "input": [1]}])
    assert errors[0]["message"] == "request body must be a JSON object"


def test_query_limit_message():
    errors = format_errors([{"type": "int_parsing", "loc": ("query", "limit"), "msg": "bad", "input": "abc"}])
    assert errors[0]["field"] == "limit"
    assert "got 'abc'" in errors[0]["message"]


def test_unknown_field_falls_back_to_the_library_message():
    errors = format_errors([{"type": "value_error", "loc": ("body", "nickname"), "msg": "too odd", "input": 1}])
    assert errors[0]["message"].startswith("nickname is invalid: too odd")


def test_duplicate_errors_are_merged():
    one = {"type": "int_type", "loc": ("body", "age"), "msg": "x", "input": "a"}
    assert len(format_errors([one, dict(one)])) == 1


def test_helpers():
    assert field_name(("body", "blood_pressure", "systolic")) == "blood_pressure.systolic"
    assert short("x" * 100).endswith("...") and len(short("x" * 100)) == 40
    assert short(5) == "5"
