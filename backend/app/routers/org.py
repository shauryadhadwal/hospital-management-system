from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..crud import create_row, delete_row, get_or_404, list_rows, update_row
from ..database import get_db
from ..schemas.org import (
    BedCreate,
    BedFree,
    BedRead,
    BedUpdate,
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
    DoctorCreate,
    DoctorRead,
    DoctorUpdate,
    RoomCreate,
    RoomRead,
    RoomUpdate,
    StaffCreate,
    StaffRead,
    StaffRole,
    StaffUpdate,
    WardCreate,
    WardRead,
    WardUpdate,
)
from ..security import get_current_staff, hash_password, require_roles

router = APIRouter(tags=["org"])


def check_doctor_staff(db: Session, staff_id: int) -> None:
    staff = get_or_404(db, models.Staff, staff_id)
    if staff.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Staff {staff_id} is not a doctor",
        )


# ---------------------------------------------------------------- departments


@router.get("/departments", response_model=List[DepartmentRead], dependencies=[Depends(get_current_staff)])
def list_departments(db: Session = Depends(get_db)):
    return list_rows(db, models.Department)


@router.get("/departments/{id}", response_model=DepartmentRead, dependencies=[Depends(get_current_staff)])
def get_department(id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Department, id)


@router.post(
    "/departments",
    response_model=DepartmentRead,
    status_code=201,
    dependencies=[Depends(require_roles("admin"))],
)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    return create_row(db, models.Department, payload.model_dump())


@router.patch("/departments/{id}", response_model=DepartmentRead, dependencies=[Depends(require_roles("admin"))])
def update_department(id: int, payload: DepartmentUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Department, id)
    return update_row(db, obj, payload.model_dump(exclude_unset=True))


@router.delete("/departments/{id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_department(id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Department, id)
    delete_row(db, obj)


# ---------------------------------------------------------------- staff


@router.get("/staff", response_model=List[StaffRead], dependencies=[Depends(get_current_staff)])
def list_staff(
    role: Optional[StaffRole] = None,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return list_rows(db, models.Staff, role=role, department_id=department_id)


@router.get("/staff/{id}", response_model=StaffRead, dependencies=[Depends(get_current_staff)])
def get_staff(id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Staff, id)


@router.post(
    "/staff",
    response_model=StaffRead,
    status_code=201,
    dependencies=[Depends(require_roles("admin"))],
)
def create_staff(payload: StaffCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    password = data.pop("password")
    if password is not None:
        data["password_hash"] = hash_password(password)
    return create_row(db, models.Staff, data)


@router.patch("/staff/{id}", response_model=StaffRead, dependencies=[Depends(require_roles("admin"))])
def update_staff(id: int, payload: StaffUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Staff, id)
    data = payload.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    if password is not None:
        data["password_hash"] = hash_password(password)
    return update_row(db, obj, data)


@router.delete("/staff/{id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_staff(id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Staff, id)
    delete_row(db, obj)


# ---------------------------------------------------------------- doctors


@router.get("/doctors", response_model=List[DoctorRead], dependencies=[Depends(get_current_staff)])
def list_doctors(staff_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.Doctor, staff_id=staff_id)


@router.get("/doctors/{id}", response_model=DoctorRead, dependencies=[Depends(get_current_staff)])
def get_doctor(id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Doctor, id)


@router.post(
    "/doctors",
    response_model=DoctorRead,
    status_code=201,
    dependencies=[Depends(require_roles("admin"))],
)
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db)):
    check_doctor_staff(db, payload.staff_id)
    return create_row(db, models.Doctor, payload.model_dump())


@router.patch("/doctors/{id}", response_model=DoctorRead, dependencies=[Depends(require_roles("admin"))])
def update_doctor(id: int, payload: DoctorUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Doctor, id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("staff_id") is not None:
        check_doctor_staff(db, data["staff_id"])
    return update_row(db, obj, data)


@router.delete("/doctors/{id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_doctor(id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Doctor, id)
    delete_row(db, obj)


# ---------------------------------------------------------------- wards


@router.get("/wards", response_model=List[WardRead], dependencies=[Depends(get_current_staff)])
def list_wards(department_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.Ward, department_id=department_id)


@router.get("/wards/{id}", response_model=WardRead, dependencies=[Depends(get_current_staff)])
def get_ward(id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Ward, id)


@router.post(
    "/wards",
    response_model=WardRead,
    status_code=201,
    dependencies=[Depends(require_roles("admin"))],
)
def create_ward(payload: WardCreate, db: Session = Depends(get_db)):
    return create_row(db, models.Ward, payload.model_dump())


@router.patch("/wards/{id}", response_model=WardRead, dependencies=[Depends(require_roles("admin"))])
def update_ward(id: int, payload: WardUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Ward, id)
    return update_row(db, obj, payload.model_dump(exclude_unset=True))


@router.delete("/wards/{id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_ward(id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Ward, id)
    delete_row(db, obj)


# ---------------------------------------------------------------- rooms


@router.get("/rooms", response_model=List[RoomRead], dependencies=[Depends(get_current_staff)])
def list_rooms(ward_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.Room, ward_id=ward_id)


@router.get("/rooms/{id}", response_model=RoomRead, dependencies=[Depends(get_current_staff)])
def get_room(id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Room, id)


@router.post(
    "/rooms",
    response_model=RoomRead,
    status_code=201,
    dependencies=[Depends(require_roles("admin"))],
)
def create_room(payload: RoomCreate, db: Session = Depends(get_db)):
    return create_row(db, models.Room, payload.model_dump())


@router.patch("/rooms/{id}", response_model=RoomRead, dependencies=[Depends(require_roles("admin"))])
def update_room(id: int, payload: RoomUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Room, id)
    return update_row(db, obj, payload.model_dump(exclude_unset=True))


@router.delete("/rooms/{id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_room(id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Room, id)
    delete_row(db, obj)


# ---------------------------------------------------------------- beds
# /beds/free must be declared before /beds/{id} so "free" is not read as an id.


@router.get("/beds", response_model=List[BedRead], dependencies=[Depends(get_current_staff)])
def list_beds(room_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.Bed, room_id=room_id)


@router.get("/beds/free", response_model=List[BedFree], dependencies=[Depends(get_current_staff)])
def list_free_beds(ward_id: Optional[int] = None, db: Session = Depends(get_db)):
    # A bed is free when no bed_assignment for it is still open (end_time IS NULL).
    open_stay = select(models.BedAssignment.id).where(
        models.BedAssignment.bed_id == models.Bed.id,
        models.BedAssignment.end_time.is_(None),
    )
    stmt = (
        select(models.Bed, models.Room, models.Ward)
        .join(models.Room, models.Bed.room_id == models.Room.id)
        .join(models.Ward, models.Room.ward_id == models.Ward.id)
        .where(~open_stay.exists())
        .order_by(models.Bed.id)
    )
    if ward_id is not None:
        stmt = stmt.where(models.Room.ward_id == ward_id)
    rows = db.execute(stmt).all()
    return [
        BedFree(
            id=bed.id,
            bed_number=bed.bed_number,
            room_id=room.id,
            room_number=room.room_number,
            room_type=room.room_type,
            daily_rate=room.daily_rate,
            ward_id=ward.id,
            ward_name=ward.name,
        )
        for bed, room, ward in rows
    ]


@router.get("/beds/{id}", response_model=BedRead, dependencies=[Depends(get_current_staff)])
def get_bed(id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Bed, id)


@router.post(
    "/beds",
    response_model=BedRead,
    status_code=201,
    dependencies=[Depends(require_roles("admin"))],
)
def create_bed(payload: BedCreate, db: Session = Depends(get_db)):
    return create_row(db, models.Bed, payload.model_dump())


@router.patch("/beds/{id}", response_model=BedRead, dependencies=[Depends(require_roles("admin"))])
def update_bed(id: int, payload: BedUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Bed, id)
    return update_row(db, obj, payload.model_dump(exclude_unset=True))


@router.delete("/beds/{id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_bed(id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Bed, id)
    delete_row(db, obj)
