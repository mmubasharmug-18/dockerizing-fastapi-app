import pytest
from pydantic import ValidationError

from app.models import VitalsIn
from tests.helpers import BOUNDARY_OK, MISSING, OUT_OF_RANGE, VALID, WRONG_TYPES, payload_with, payload_without


def failed_fields(payload):
    with pytest.raises(ValidationError) as info:
        VitalsIn.model_validate(payload)
    return {".".join(str(p) for p in e["loc"]) for e in info.value.errors()}


def test_valid_payload_is_accepted():
    vitals = VitalsIn.model_validate(VALID)
    assert vitals.patient_id == "P-1001"
    assert vitals.blood_pressure.systolic == 120


def test_whole_number_glucose_is_accepted():
    assert VitalsIn.model_validate(payload_with("glucose_level", 95)).glucose_level == 95.0


def test_patient_id_is_trimmed():
    assert VitalsIn.model_validate(payload_with("patient_id", "  P-7  ")).patient_id == "P-7"


@pytest.mark.parametrize("path,value", BOUNDARY_OK)
def test_boundary_values_are_accepted(path, value):
    VitalsIn.model_validate(payload_with(path, value))


@pytest.mark.parametrize("path,value", OUT_OF_RANGE)
def test_out_of_range_is_rejected(path, value):
    assert failed_fields(payload_with(path, value)) == {path}


@pytest.mark.parametrize("path,value", WRONG_TYPES)
def test_wrong_types_are_rejected(path, value):
    assert path in failed_fields(payload_with(path, value))


@pytest.mark.parametrize("path", MISSING)
def test_missing_fields_are_rejected(path):
    assert path in failed_fields(payload_without(path))


def test_nan_glucose_is_rejected():
    assert failed_fields(payload_with("glucose_level", float("nan"))) == {"glucose_level"}
