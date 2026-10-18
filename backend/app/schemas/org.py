from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

StaffRole = Literal["doctor", "receptionist", "nurse", "lab", "admin"]
RoomType = Literal["private", "shared"]


# ---------------------------------------------------------------- department


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)


class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- staff
# Password is accepted as plain `password` on write and hashed by the router.
# StaffRead has no password_hash field, so it is never returned.


class StaffCreate(BaseModel):
    department_id: int
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    role: StaffRole
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    hire_date: date
    username: Optional[str] = Field(default=None, max_length=50)
    login_enabled: bool = False
    password: Optional[str] = None


class StaffUpdate(BaseModel):
    department_id: Optional[int] = None
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    role: Optional[StaffRole] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    hire_date: Optional[date] = None
    username: Optional[str] = Field(default=None, max_length=50)
    login_enabled: Optional[bool] = None
    password: Optional[str] = None


class StaffRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_id: int
    first_name: str
    last_name: str
    role: str
    phone: Optional[str] = None
    email: Optional[str] = None
    hire_date: date
    username: Optional[str] = None
    login_enabled: bool
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- doctor


class DoctorCreate(BaseModel):
    staff_id: int
    license_number: str = Field(min_length=1, max_length=50)
    specialty: str = Field(min_length=1, max_length=100)
    consultation_fee: Decimal = Field(ge=0)


class DoctorUpdate(BaseModel):
    staff_id: Optional[int] = None
    license_number: Optional[str] = Field(default=None, min_length=1, max_length=50)
    specialty: Optional[str] = Field(default=None, min_length=1, max_length=100)
    consultation_fee: Optional[Decimal] = Field(default=None, ge=0)


class DoctorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    staff_id: int
    license_number: str
    specialty: str
    consultation_fee: Decimal
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- ward


class WardCreate(BaseModel):
    department_id: int
    name: str = Field(min_length=1, max_length=100)


class WardUpdate(BaseModel):
    department_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)


class WardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_id: int
    name: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- room


class RoomCreate(BaseModel):
    ward_id: int
    room_number: str = Field(min_length=1, max_length=20)
    room_type: RoomType
    daily_rate: Decimal = Field(ge=0)


class RoomUpdate(BaseModel):
    ward_id: Optional[int] = None
    room_number: Optional[str] = Field(default=None, min_length=1, max_length=20)
    room_type: Optional[RoomType] = None
    daily_rate: Optional[Decimal] = Field(default=None, ge=0)


class RoomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ward_id: int
    room_number: str
    room_type: str
    daily_rate: Decimal
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- bed


class BedCreate(BaseModel):
    room_id: int
    bed_number: str = Field(min_length=1, max_length=20)


class BedUpdate(BaseModel):
    room_id: Optional[int] = None
    bed_number: Optional[str] = Field(default=None, min_length=1, max_length=20)


class BedRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    bed_number: str
    created_at: datetime
    updated_at: datetime


class BedFree(BaseModel):
    id: int
    bed_number: str
    room_id: int
    room_number: str
    room_type: str
    daily_rate: Decimal
    ward_id: int
    ward_name: str
