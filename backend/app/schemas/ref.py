from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------- procedures


class ProcedureCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(ge=0)


class ProcedureUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(default=None, ge=0)


class ProcedureRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- medications


class MedicationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    form: str = Field(min_length=1, max_length=30)
    strength: str = Field(min_length=1, max_length=30)
    price: Decimal = Field(ge=0)


class MedicationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    form: Optional[str] = Field(default=None, min_length=1, max_length=30)
    strength: Optional[str] = Field(default=None, min_length=1, max_length=30)
    price: Optional[Decimal] = Field(default=None, ge=0)


class MedicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    form: str
    strength: str
    price: Decimal
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- lab tests


class LabTestCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(ge=0)


class LabTestUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(default=None, ge=0)


class LabTestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- consumables


class ConsumableCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    unit: str = Field(min_length=1, max_length=30)
    price: Decimal = Field(ge=0)


class ConsumableUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    unit: Optional[str] = Field(default=None, min_length=1, max_length=30)
    price: Optional[Decimal] = Field(default=None, ge=0)


class ConsumableRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    unit: str
    price: Decimal
    created_at: datetime
    updated_at: datetime
