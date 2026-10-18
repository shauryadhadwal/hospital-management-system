from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models
from .crud import get_or_404


def _bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def invoice_total(db: Session, invoice: models.Invoice) -> Decimal:
    lines = db.scalars(
        select(models.InvoiceLine).where(models.InvoiceLine.invoice_id == invoice.id)
    ).all()
    return sum((line.quantity * line.unit_price for line in lines), Decimal("0"))


def paid_claims(db: Session, invoice: models.Invoice) -> Decimal:
    claims = db.scalars(
        select(models.InsuranceClaim).where(
            models.InsuranceClaim.invoice_id == invoice.id,
            models.InsuranceClaim.status == "paid",
        )
    ).all()
    return sum((claim.amount_claimed for claim in claims), Decimal("0"))


def payments_total(db: Session, invoice: models.Invoice) -> Decimal:
    payments = db.scalars(
        select(models.Payment).where(models.Payment.invoice_id == invoice.id)
    ).all()
    return sum((payment.amount for payment in payments), Decimal("0"))


def balance(db: Session, invoice: models.Invoice) -> Decimal:
    return invoice_total(db, invoice) - paid_claims(db, invoice) - payments_total(db, invoice)


def mark_paid_if_settled(db: Session, invoice: models.Invoice) -> None:
    # Caller commits.
    if invoice.status == "issued" and balance(db, invoice) == 0:
        invoice.status = "paid"


def bed_days(db: Session, stay: models.BedAssignment) -> int:
    if stay.end_time is None:
        raise _bad_request("This bed stay is still open; it can be billed once it ends")
    days = (stay.end_time.date() - stay.start_time.date()).days + 1
    transfer = db.scalar(
        select(models.BedAssignment.id).where(
            models.BedAssignment.visit_id == stay.visit_id,
            models.BedAssignment.start_time == stay.end_time,
        )
    )
    if transfer is not None:
        days -= 1
    return max(days, 1)


def next_invoice_number(db: Session, year: int) -> str:
    prefix = "INV-{}-".format(year)
    count = db.scalar(
        select(func.count())
        .select_from(models.Invoice)
        .where(models.Invoice.invoice_number.startswith(prefix))
    )
    return "{}{:06d}".format(prefix, count + 1)


def _check_source(db: Session, invoice: models.Invoice, source_type: str, source_id: int, visit_id: int) -> None:
    if visit_id != invoice.visit_id:
        raise _bad_request("This {} belongs to a different visit than the invoice".format(source_type))
    billed = db.scalar(
        select(models.InvoiceLine.id).where(
            models.InvoiceLine.source_type == source_type,
            models.InvoiceLine.source_id == source_id,
        )
    )
    if billed is not None:
        raise _bad_request("This {} {} is already billed".format(source_type, source_id))


def line_from_source(
    db: Session, invoice: models.Invoice, source_type: str, source_id: int
) -> dict:
    if source_type == "bed_assignment":
        stay = get_or_404(db, models.BedAssignment, source_id, "Bed assignment")
        _check_source(db, invoice, source_type, source_id, stay.visit_id)
        bed = db.get(models.Bed, stay.bed_id)
        room = bed.room
        return {
            "description": "Bed days: {} room {} bed {}".format(
                room.ward.name, room.room_number, bed.bed_number
            ),
            "quantity": bed_days(db, stay),
            "unit_price": room.daily_rate,
        }

    if source_type == "lab_order":
        order = get_or_404(db, models.LabOrder, source_id, "Lab order")
        _check_source(db, invoice, source_type, source_id, order.visit_id)
        return {
            "description": "Lab test: {}".format(order.lab_test.name),
            "quantity": 1,
            "unit_price": order.lab_test.price,
        }

    usage = get_or_404(db, models.ConsumableUsage, source_id, "Consumable usage")
    _check_source(db, invoice, source_type, source_id, usage.visit_id)
    consumable = db.get(models.Consumable, usage.consumable_id)
    return {
        "description": "Consumable: {}".format(consumable.name),
        "quantity": usage.quantity,
        "unit_price": consumable.price,
    }
