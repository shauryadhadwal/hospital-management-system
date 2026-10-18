from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..billing import (
    balance,
    invoice_total,
    line_from_source,
    mark_paid_if_settled,
    next_invoice_number,
    paid_claims,
    payments_total,
)
from ..crud import commit_or_409, create_row, delete_row, get_or_404, list_rows, update_row
from ..database import get_db
from ..schemas.billing import (
    InsuranceClaimApprove,
    InsuranceClaimCreate,
    InsuranceClaimPay,
    InsuranceClaimRead,
    InvoiceCreate,
    InvoiceDetail,
    InvoiceLineCreate,
    InvoiceLineRead,
    InvoiceRead,
    InvoiceStatus,
    PaymentCreate,
    PaymentRead,
)
from ..security import get_current_staff, require_roles

router = APIRouter(tags=["billing"])


def _bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def _invoice_detail(db: Session, invoice: models.Invoice) -> InvoiceDetail:
    lines = list_rows(db, models.InvoiceLine, invoice_id=invoice.id)
    return InvoiceDetail(
        **InvoiceRead.model_validate(invoice).model_dump(),
        lines=[InvoiceLineRead.model_validate(line) for line in lines],
        total=invoice_total(db, invoice),
        paid_claims=paid_claims(db, invoice),
        payments=payments_total(db, invoice),
        balance=balance(db, invoice),
    )


# ---------------------------------------------------------------- invoices


@router.get(
    "/invoices",
    response_model=List[InvoiceRead],
    dependencies=[Depends(get_current_staff)],
)
def list_invoices(
    visit_id: Optional[int] = None,
    status: Optional[InvoiceStatus] = None,
    db: Session = Depends(get_db),
):
    return list_rows(db, models.Invoice, visit_id=visit_id, status=status)


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceDetail,
    dependencies=[Depends(get_current_staff)],
)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = get_or_404(db, models.Invoice, invoice_id, "Invoice")
    return _invoice_detail(db, invoice)


@router.post(
    "/invoices",
    response_model=InvoiceDetail,
    dependencies=[Depends(require_roles("receptionist"))],
)
def create_invoice(body: InvoiceCreate, db: Session = Depends(get_db)):
    visit = get_or_404(db, models.Visit, body.visit_id, "Visit")
    if visit.status != "completed":
        raise _bad_request("An invoice can only be made for a completed visit")
    existing = db.scalar(select(models.Invoice.id).where(models.Invoice.visit_id == visit.id))
    if existing is not None:
        raise _bad_request("This visit already has an invoice")
    today = date.today()
    invoice = create_row(
        db,
        models.Invoice,
        {
            "visit_id": visit.id,
            "invoice_number": next_invoice_number(db, today.year),
            "invoice_date": today,
            "status": "draft",
        },
    )
    return _invoice_detail(db, invoice)


@router.post(
    "/invoices/{invoice_id}/issue",
    response_model=InvoiceDetail,
    dependencies=[Depends(require_roles("receptionist"))],
)
def issue_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = get_or_404(db, models.Invoice, invoice_id, "Invoice")
    if invoice.status != "draft":
        raise _bad_request("Only a draft invoice can be issued")
    if not list_rows(db, models.InvoiceLine, invoice_id=invoice.id):
        raise _bad_request("An invoice needs at least one line before it can be issued")
    update_row(db, invoice, {"status": "issued"})
    return _invoice_detail(db, invoice)


# ---------------------------------------------------------------- invoice lines


@router.get(
    "/invoice-lines",
    response_model=List[InvoiceLineRead],
    dependencies=[Depends(get_current_staff)],
)
def list_invoice_lines(invoice_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.InvoiceLine, invoice_id=invoice_id)


@router.post(
    "/invoice-lines",
    response_model=InvoiceLineRead,
    dependencies=[Depends(require_roles("receptionist"))],
)
def create_invoice_line(body: InvoiceLineCreate, db: Session = Depends(get_db)):
    invoice = get_or_404(db, models.Invoice, body.invoice_id, "Invoice")
    if invoice.status != "draft":
        raise _bad_request("Lines can only be added to a draft invoice")
    if (body.source_type is None) != (body.source_id is None):
        raise _bad_request("source_type and source_id must be given together")

    if body.source_type is not None:
        values = line_from_source(db, invoice, body.source_type, body.source_id)
    else:
        if not body.description or not body.description.strip():
            raise _bad_request("description is required for a line without a source")
        if body.quantity is None or body.quantity <= 0:
            raise _bad_request("quantity must be greater than 0 for a line without a source")
        if body.unit_price is None or body.unit_price < 0:
            raise _bad_request("unit_price must be 0 or more for a line without a source")
        values = {
            "description": body.description,
            "quantity": body.quantity,
            "unit_price": body.unit_price,
        }

    data = {
        "invoice_id": invoice.id,
        "source_type": body.source_type,
        "source_id": body.source_id,
        **values,
    }
    return create_row(db, models.InvoiceLine, data)


@router.delete(
    "/invoice-lines/{line_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("receptionist"))],
)
def delete_invoice_line(line_id: int, db: Session = Depends(get_db)):
    line = get_or_404(db, models.InvoiceLine, line_id, "Invoice line")
    invoice = get_or_404(db, models.Invoice, line.invoice_id, "Invoice")
    if invoice.status != "draft":
        raise _bad_request("Lines can only be removed from a draft invoice")
    delete_row(db, line)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------- payments


@router.get(
    "/payments",
    response_model=List[PaymentRead],
    dependencies=[Depends(get_current_staff)],
)
def list_payments(invoice_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.Payment, invoice_id=invoice_id)


@router.post(
    "/payments",
    response_model=PaymentRead,
    dependencies=[Depends(require_roles("receptionist"))],
)
def create_payment(body: PaymentCreate, db: Session = Depends(get_db)):
    invoice = get_or_404(db, models.Invoice, body.invoice_id, "Invoice")
    if invoice.status != "issued":
        raise _bad_request("Payments can only be recorded on an issued invoice")
    current = balance(db, invoice)
    if body.amount > current:
        raise _bad_request(
            "Amount {} is more than the balance {}".format(body.amount, current)
        )
    payment = models.Payment(
        invoice_id=invoice.id,
        amount=body.amount,
        paid_at=body.paid_at or date.today(),
        method=body.method,
        reference=body.reference,
    )
    db.add(payment)
    mark_paid_if_settled(db, invoice)
    commit_or_409(db)
    db.refresh(payment)
    return payment


# ---------------------------------------------------------------- insurance claims


@router.get(
    "/insurance-claims",
    response_model=List[InsuranceClaimRead],
    dependencies=[Depends(get_current_staff)],
)
def list_insurance_claims(invoice_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.InsuranceClaim, invoice_id=invoice_id)


@router.get(
    "/insurance-claims/{claim_id}",
    response_model=InsuranceClaimRead,
    dependencies=[Depends(get_current_staff)],
)
def get_insurance_claim(claim_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.InsuranceClaim, claim_id, "Insurance claim")


@router.post(
    "/insurance-claims",
    response_model=InsuranceClaimRead,
    dependencies=[Depends(require_roles("receptionist"))],
)
def create_insurance_claim(body: InsuranceClaimCreate, db: Session = Depends(get_db)):
    invoice = get_or_404(db, models.Invoice, body.invoice_id, "Invoice")
    if invoice.status != "issued":
        raise _bad_request("Claims can only be made on an issued invoice")
    policy = get_or_404(db, models.InsurancePolicy, body.policy_id, "Insurance policy")
    visit = get_or_404(db, models.Visit, invoice.visit_id, "Visit")
    if policy.patient_id != visit.patient_id:
        raise _bad_request("The policy does not belong to the patient of this visit")
    visit_date = (visit.actual_start or visit.planned_start).date()
    if not (policy.valid_from <= visit_date <= policy.valid_to):
        raise _bad_request(
            "The policy was not valid on the visit date {}".format(visit_date)
        )
    total = invoice_total(db, invoice)
    if body.amount_claimed > total:
        raise _bad_request(
            "Amount claimed {} is more than the invoice total {}".format(body.amount_claimed, total)
        )
    return create_row(
        db,
        models.InsuranceClaim,
        {
            "invoice_id": invoice.id,
            "policy_id": policy.id,
            "amount_claimed": body.amount_claimed,
            "status": "submitted",
            "submitted_date": body.submitted_date or date.today(),
        },
    )


@router.post(
    "/insurance-claims/{claim_id}/approve",
    response_model=InsuranceClaimRead,
    dependencies=[Depends(require_roles("receptionist"))],
)
def approve_insurance_claim(
    claim_id: int,
    body: Optional[InsuranceClaimApprove] = None,
    db: Session = Depends(get_db),
):
    claim = get_or_404(db, models.InsuranceClaim, claim_id, "Insurance claim")
    if claim.status != "submitted":
        raise _bad_request("Only a submitted claim can be approved")
    approved_date = (body and body.approved_date) or date.today()
    return update_row(db, claim, {"status": "approved", "approved_date": approved_date})


@router.post(
    "/insurance-claims/{claim_id}/pay",
    response_model=InsuranceClaimRead,
    dependencies=[Depends(require_roles("receptionist"))],
)
def pay_insurance_claim(
    claim_id: int,
    body: Optional[InsuranceClaimPay] = None,
    db: Session = Depends(get_db),
):
    claim = get_or_404(db, models.InsuranceClaim, claim_id, "Insurance claim")
    if claim.status != "approved":
        raise _bad_request("Only an approved claim can be paid")
    invoice = get_or_404(db, models.Invoice, claim.invoice_id, "Invoice")
    current = balance(db, invoice)
    if claim.amount_claimed > current:
        raise _bad_request(
            "Claim amount {} is more than the balance {}".format(claim.amount_claimed, current)
        )
    claim.status = "paid"
    claim.paid_date = (body and body.paid_date) or date.today()
    mark_paid_if_settled(db, invoice)
    commit_or_409(db)
    db.refresh(claim)
    return claim
