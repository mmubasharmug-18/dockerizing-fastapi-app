import copy

VALID = {
    "patient_id": "P-1001",
    "age": 45,
    "blood_pressure": {"systolic": 120, "diastolic": 80},
    "glucose_level": 95.5,
}

OUT_OF_RANGE = [
    ("age", -1),
    ("age", 121),
    ("blood_pressure.systolic", 49),
    ("blood_pressure.systolic", 301),
    ("blood_pressure.diastolic", 29),
    ("blood_pressure.diastolic", 201),
    ("glucose_level", 0),
    ("glucose_level", -5.5),
]

BOUNDARY_OK = [
    ("age", 0),
    ("age", 120),
    ("blood_pressure.systolic", 50),
    ("blood_pressure.systolic", 300),
    ("blood_pressure.diastolic", 30),
    ("blood_pressure.diastolic", 200),
    ("glucose_level", 0.1),
    ("glucose_level", 100),
]

WRONG_TYPES = [
    ("age", "30"),
    ("age", 30.5),
    ("age", True),
    ("age", None),
    ("age", [30]),
    ("blood_pressure.systolic", "120"),
    ("blood_pressure.systolic", 120.5),
    ("blood_pressure.diastolic", "80"),
    ("blood_pressure.diastolic", None),
    ("glucose_level", "95"),
    ("glucose_level", True),
    ("glucose_level", None),
    ("glucose_level", []),
    ("patient_id", 123),
    ("patient_id", None),
    ("patient_id", ""),
    ("patient_id", "   "),
    ("blood_pressure", "120/80"),
    ("blood_pressure", [120, 80]),
]

MISSING = [
    "patient_id",
    "age",
    "blood_pressure",
    "blood_pressure.systolic",
    "blood_pressure.diastolic",
    "glucose_level",
]


def _walk(payload, path):
    *parents, last = path.split(".")
    target = payload
    for key in parents:
        target = target[key]
    return target, last


def payload_with(path, value):
    payload = copy.deepcopy(VALID)
    target, last = _walk(payload, path)
    target[last] = value
    return payload


def payload_without(path):
    payload = copy.deepcopy(VALID)
    target, last = _walk(payload, path)
    del target[last]
    return payload
