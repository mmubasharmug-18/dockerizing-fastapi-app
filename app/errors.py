FIELD_MESSAGES = {
    "patient_id": "patient_id is required and must be a non-empty string",
    "age": "age must be an integer between 0 and 120",
    "blood_pressure": "blood_pressure is required and must be an object with systolic and diastolic",
    "blood_pressure.systolic": "blood_pressure.systolic must be an integer between 50 and 300",
    "blood_pressure.diastolic": "blood_pressure.diastolic must be an integer between 30 and 200",
    "glucose_level": "glucose_level must be a number greater than 0",
    "limit": "limit must be a whole number greater than 0",
}

LOCATION_NAMES = {"body", "query", "path"}


def short(value) -> str:
    text = repr(value)
    return text if len(text) <= 40 else text[:37] + "..."


def field_name(loc) -> str:
    return ".".join(str(part) for part in loc if part not in LOCATION_NAMES)


def describe(error: dict) -> dict:
    kind = error.get("type")
    if kind == "json_invalid":
        return {"field": "body", "message": "request body must be valid JSON"}

    name = field_name(error.get("loc", ()))
    if name == "":
        if kind == "missing":
            return {"field": "body", "message": "request body is required"}
        return {"field": "body", "message": "request body must be a JSON object"}

    message = FIELD_MESSAGES.get(name) or f"{name} is invalid: {error.get('msg')}"
    if kind == "missing":
        message += " (field is missing)"
    else:
        message += f" (got {short(error.get('input'))})"
    return {"field": name, "message": message}


def format_errors(errors: list) -> list:
    seen = set()
    result = []
    for error in errors:
        item = describe(error)
        key = (item["field"], item["message"])
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result
