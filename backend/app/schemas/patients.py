from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Sex = Literal["male", "female", "other"]


# ---------------------------------------------------------------- patient


class PatientCreate(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    age: int = Field(ge=0, le=130)
    sex: Sex
    phone: str = Field(max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=255)
    emergency_contact_name: Optional[str] = Field(default=None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(default=None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(default=None, max_length=50)


class PatientUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    age: Optional[int] = Field(default=None, ge=0, le=130)
    sex: Optional[Sex] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=255)
    emergency_contact_name: Optional[str] = Field(default=None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(default=None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(default=None, max_length=50)


class PatientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    sex: Sex
    phone: str
    email: Optional[str]
    address: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    emergency_contact_relationship: Optional[str]
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- insurance


class InsuranceProviderCreate(BaseModel):
    name: str = Field(max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)


class InsuranceProviderUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)


class InsuranceProviderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    created_at: datetime
    updated_at: datetime


class InsurancePolicyCreate(BaseModel):
    patient_id: int
    provider_id: int
    policy_number: str = Field(max_length=50)
    valid_from: date
    valid_to: date


class InsurancePolicyUpdate(BaseModel):
    provider_id: Optional[int] = None
    policy_number: Optional[str] = Field(default=None, max_length=50)
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None


class InsurancePolicyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    provider_id: int
    policy_number: str
    valid_from: date
    valid_to: date
    created_at: datetime
    updated_at: datetime
