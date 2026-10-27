"""
Procure-to-Pay (P2P) normalized transactional models for audit_copilot.
"""

import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Text, Numeric, Date, DateTime, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.session import Base

SCHEMA = "audit_copilot"


class P2PSupplier(Base):
    __tablename__ = "p2p_suppliers"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_datasets.id"), nullable=False)
    source_dataset_row_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.dataset_rows.id"), nullable=True)
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    source_locator = Column(JSONB, nullable=False, default=dict)
    supplier_code = Column(String, nullable=True)
    supplier_name = Column(Text, nullable=False)
    tax_identifier = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="active")
    attributes = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class P2PPurchaseOrder(Base):
    __tablename__ = "p2p_purchase_orders"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_datasets.id"), nullable=False)
    source_dataset_row_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.dataset_rows.id"), nullable=True)
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    source_locator = Column(JSONB, nullable=False, default=dict)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_suppliers.id"), nullable=True)
    po_number = Column(String, nullable=False)
    order_date = Column(Date, nullable=True)
    currency_code = Column(String(3), nullable=True, default="USD")
    status = Column(String, nullable=False, default="approved")
    total_amount = Column(Numeric, nullable=True)
    attributes = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class P2PPurchaseOrderLine(Base):
    __tablename__ = "p2p_purchase_order_lines"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_purchase_orders.id"), nullable=False)
    line_number = Column(String, nullable=True)
    item_code = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    ordered_quantity = Column(Numeric, nullable=True)
    unit_of_measure = Column(String, nullable=True)
    unit_price = Column(Numeric, nullable=True)
    line_amount = Column(Numeric, nullable=True)
    tax_amount = Column(Numeric, nullable=True)
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    source_locator = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class P2PGoodsReceipt(Base):
    __tablename__ = "p2p_goods_receipts"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_datasets.id"), nullable=False)
    source_dataset_row_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.dataset_rows.id"), nullable=True)
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    source_locator = Column(JSONB, nullable=False, default=dict)
    receipt_number = Column(String, nullable=True)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_purchase_orders.id"), nullable=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_suppliers.id"), nullable=True)
    receipt_date = Column(Date, nullable=True)
    status = Column(String, nullable=False, default="received")
    attributes = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class P2PGoodsReceiptLine(Base):
    __tablename__ = "p2p_goods_receipt_lines"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    goods_receipt_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_goods_receipts.id"), nullable=False)
    purchase_order_line_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_purchase_order_lines.id"), nullable=True)
    line_number = Column(String, nullable=True)
    item_code = Column(String, nullable=True)
    received_quantity = Column(Numeric, nullable=True)
    unit_of_measure = Column(String, nullable=True)
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    source_locator = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class P2PInvoice(Base):
    __tablename__ = "p2p_invoices"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_datasets.id"), nullable=False)
    source_dataset_row_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.dataset_rows.id"), nullable=True)
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    source_locator = Column(JSONB, nullable=False, default=dict)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_suppliers.id"), nullable=True)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_purchase_orders.id"), nullable=True)
    invoice_number = Column(String, nullable=True)
    normalized_invoice_number = Column(String, nullable=True)
    invoice_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    currency_code = Column(String(3), nullable=True, default="USD")
    subtotal_amount = Column(Numeric, nullable=True)
    tax_amount = Column(Numeric, nullable=True)
    total_amount = Column(Numeric, nullable=True)
    status = Column(String, nullable=False, default="approved")
    attributes = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class P2PInvoiceLine(Base):
    __tablename__ = "p2p_invoice_lines"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_invoices.id"), nullable=False)
    purchase_order_line_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_purchase_order_lines.id"), nullable=True)
    line_number = Column(String, nullable=True)
    item_code = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    invoiced_quantity = Column(Numeric, nullable=True)
    unit_of_measure = Column(String, nullable=True)
    unit_price = Column(Numeric, nullable=True)
    line_amount = Column(Numeric, nullable=True)
    tax_amount = Column(Numeric, nullable=True)
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    source_locator = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class P2PPayment(Base):
    __tablename__ = "p2p_payments"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_datasets.id"), nullable=False)
    source_dataset_row_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.dataset_rows.id"), nullable=True)
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    source_locator = Column(JSONB, nullable=False, default=dict)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_suppliers.id"), nullable=True)
    payment_reference = Column(String, nullable=True)
    payment_date = Column(Date, nullable=True)
    currency_code = Column(String(3), nullable=True, default="USD")
    amount = Column(Numeric, nullable=False)
    payment_method = Column(String, nullable=True)
    status = Column(String, nullable=False, default="cleared")
    attributes = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class P2PPaymentAllocation(Base):
    __tablename__ = "p2p_payment_allocations"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    payment_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_payments.id"), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_invoices.id"), nullable=False)
    allocated_amount = Column(Numeric, nullable=False)
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    source_locator = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class P2PApprovalEvent(Base):
    __tablename__ = "p2p_approval_events"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_purchase_orders.id"), nullable=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_invoices.id"), nullable=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_payments.id"), nullable=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.p2p_suppliers.id"), nullable=True)
    event_type = Column(String, nullable=False, default="po_approval")
    decision = Column(String, nullable=True, default="approved")
    approver_user_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    approver_external_id = Column(String, nullable=True)
    approver_name = Column(Text, nullable=True)
    approval_reference = Column(String, nullable=True)
    event_at = Column(DateTime(timezone=True), nullable=True)
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    source_locator = Column(JSONB, nullable=False, default=dict)
    attributes = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

