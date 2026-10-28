from datetime import datetime

from pydantic import BaseModel, Field, StrictInt, StrictStr, field_validator


class BloodPressure(BaseModel):
    systolic: StrictInt = Field(ge=50, le=300, examples=[120])
    diastolic: StrictInt = Field(ge=30, le=200, examples=[80])


class VitalsIn(BaseModel):
    patient_id: StrictStr = Field(min_length=1, examples=["P-1001"])
    age: StrictInt = Field(ge=0, le=120, examples=[45])
    blood_pressure: BloodPressure
    glucose_level: float = Field(gt=0, allow_inf_nan=False, examples=[95.5])

    @field_validator("patient_id", mode="before")
    @classmethod
    def strip_patient_id(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("glucose_level", mode="before")
    @classmethod
    def only_real_numbers(cls, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("glucose_level must be a number")
        return value


class VitalsOut(VitalsIn):
    id: int
    recorded_at: datetime


class Averages(BaseModel):
    systolic: float
    diastolic: float
    glucose: float


class SummaryOut(BaseModel):
    patient_id: str
    record_count: int
    averages: Averages


class HealthOut(BaseModel):
    status: str
    timestamp: datetime
