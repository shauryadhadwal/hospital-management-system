from datetime import date, datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

InvoiceStatus = Literal["draft", "issued", "paid", "cancelled"]
SourceType = Literal["bed_assignment", "lab_order", "consumable_usage"]
PaymentMethod = Literal["cash", "card", "UPI", "bank transfer"]
ClaimStatus = Literal["submitted", "approved", "rejected", "paid"]


# ---------------------------------------------------------------- invoice


class InvoiceCreate(BaseModel):
    visit_id: int


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int
    invoice_number: str
    invoice_date: date
    status: InvoiceStatus
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- invoice line


class InvoiceLineCreate(BaseModel):
    invoice_id: int
    source_type: Optional[SourceType] = None
    source_id: Optional[int] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None


class InvoiceLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    source_type: Optional[SourceType]
    source_id: Optional[int]
    description: str
    quantity: int
    unit_price: Decimal
    created_at: datetime
    updated_at: datetime


class InvoiceDetail(InvoiceRead):
    lines: List[InvoiceLineRead]
    total: Decimal
    paid_claims: Decimal
    payments: Decimal
    balance: Decimal


# ---------------------------------------------------------------- payment


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: Decimal = Field(gt=0)
    paid_at: Optional[date] = None
    method: PaymentMethod
    reference: Optional[str] = None


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    amount: Decimal
    paid_at: date
    method: PaymentMethod
    reference: Optional[str]
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- insurance claim


class InsuranceClaimCreate(BaseModel):
    invoice_id: int
    policy_id: int
    amount_claimed: Decimal = Field(gt=0)
    submitted_date: Optional[date] = None


class InsuranceClaimApprove(BaseModel):
    approved_date: Optional[date] = None


class InsuranceClaimPay(BaseModel):
    paid_date: Optional[date] = None


class InsuranceClaimRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    policy_id: int
    amount_claimed: Decimal
    status: ClaimStatus
    submitted_date: date
    approved_date: Optional[date]
    paid_date: Optional[date]
    created_at: datetime
    updated_at: datetime
