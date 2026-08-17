"""
modules/module1_leads.py
Module 1 - Lead Management & Prospect Database

Full CRUD for leads (prospects), plus basic engagement-history logging
(sales_interactions). This is the source of truth all other modules
(2, 3, 4, 5, 6) read from.

Mounted in main.py as:
    app.include_router(leads_router, prefix="/leads", tags=["Module 1 - Leads"])
"""

import csv
import io
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database.connection import get_db
from database.models import Lead, SalesInteraction

router = APIRouter()


# --------------------------------------------------------------------------
# SCHEMAS
# --------------------------------------------------------------------------
class LeadCreate(BaseModel):
    company_name: str
    industry: Optional[str] = None
    contact_name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[str] = None
    location: Optional[str] = None
    funding_stage: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    lead_status: str = "New"
    segment: Optional[str] = None  # Enterprise / Mid-Market / Startup
    deal_value: Optional[int] = None  # estimated deal size in USD


class LeadUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    contact_name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[str] = None
    location: Optional[str] = None
    funding_stage: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    lead_status: Optional[str] = None
    segment: Optional[str] = None
    deal_value: Optional[int] = None


class LeadOut(BaseModel):
    lead_id: int
    company_name: str
    industry: Optional[str] = None
    contact_name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[str] = None
    location: Optional[str] = None
    funding_stage: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    lead_status: Optional[str] = None
    segment: Optional[str] = None
    deal_value: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LeadImportRow(BaseModel):
    company_name: str
    industry: Optional[str] = None
    contact_name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[str] = None
    location: Optional[str] = None
    funding_stage: Optional[str] = None
    lead_status: Optional[str] = "New"
    segment: Optional[str] = None
    deal_value: Optional[int] = None
    tech_stack: Optional[List[str]] = None


class ImportResult(BaseModel):
    row: int
    status: str
    company_name: Optional[str] = None
    detail: Optional[str] = None


class ImportSummary(BaseModel):
    total_rows: int
    created: int
    duplicates: int
    errors: int
    results: List[ImportResult]


class InteractionCreate(BaseModel):
    interaction_type: str  # Call / Email / Meeting / Note
    summary: Optional[str] = None
    action_items: Optional[str] = None


class InteractionOut(BaseModel):
    interaction_id: int
    lead_id: int
    interaction_type: str
    summary: Optional[str] = None
    action_items: Optional[str] = None
    interaction_date: Optional[datetime] = None

    class Config:
        from_attributes = True


LEAD_STAGES = ["New", "Contacted", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]


# --------------------------------------------------------------------------
# LEAD CRUD ROUTES
# --------------------------------------------------------------------------
@router.get("/stages")
def get_stages():
    """Lifecycle stages the frontend can render as a dropdown."""
    return {"stages": LEAD_STAGES}


@router.post("", response_model=LeadOut)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(**payload.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def _optional_text(value: object) -> Optional[str]:
    """Normalize optional text values received from CSV or manual import."""
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _parse_deal_value(value: object) -> Optional[int]:
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(float(str(value).replace("$", "").replace(",", "").strip()))
    except ValueError as exc:
        raise ValueError("deal_value must be a whole number.") from exc


def _lead_from_import_row(row: LeadImportRow) -> Lead:
    company_name = row.company_name.strip()
    if not company_name:
        raise ValueError("company_name is required.")

    lead_status = _optional_text(row.lead_status) or "New"
    if lead_status not in LEAD_STAGES:
        raise ValueError(f"lead_status must be one of: {', '.join(LEAD_STAGES)}.")

    return Lead(
        company_name=company_name,
        industry=_optional_text(row.industry),
        contact_name=_optional_text(row.contact_name),
        title=_optional_text(row.title),
        email=_optional_text(row.email),
        phone=_optional_text(row.phone),
        company_size=_optional_text(row.company_size),
        annual_revenue=_optional_text(row.annual_revenue),
        location=_optional_text(row.location),
        funding_stage=_optional_text(row.funding_stage),
        lead_status=lead_status,
        segment=_optional_text(row.segment),
        deal_value=row.deal_value,
        tech_stack=row.tech_stack,
    )


def _duplicate_lead(db: Session, company_name: str, email: Optional[str]) -> bool:
    if email:
        return db.query(Lead).filter(Lead.email.ilike(email)).first() is not None
    return db.query(Lead).filter(Lead.company_name.ilike(company_name)).first() is not None


def _import_leads(rows: List[LeadImportRow], db: Session, row_numbers: Optional[List[int]] = None) -> ImportSummary:
    results: List[ImportResult] = []
    created = duplicates = errors = 0
    seen_emails = set()
    seen_companies_without_email = set()

    for index, row in enumerate(rows):
        row_number = row_numbers[index] if row_numbers else index + 1
        company_name = _optional_text(row.company_name)
        email = _optional_text(row.email)
        try:
            if not company_name:
                raise ValueError("company_name is required.")

            duplicate_key = email.lower() if email else company_name.lower()
            batch_duplicates = seen_emails if email else seen_companies_without_email
            if duplicate_key in batch_duplicates or _duplicate_lead(db, company_name, email):
                duplicates += 1
                results.append(ImportResult(row=row_number, status="duplicate", company_name=company_name,
                                            detail="A matching lead already exists."))
                continue

            lead = _lead_from_import_row(row)
            db.add(lead)
            db.flush()
            batch_duplicates.add(duplicate_key)
            created += 1
            results.append(ImportResult(row=row_number, status="created", company_name=lead.company_name))
        except (TypeError, ValueError) as exc:
            errors += 1
            results.append(ImportResult(row=row_number, status="error", company_name=company_name, detail=str(exc)))

    db.commit()
    return ImportSummary(total_rows=len(rows), created=created, duplicates=duplicates, errors=errors, results=results)


@router.post("/import/manual", response_model=ImportSummary)
def import_manual_leads(rows: List[LeadImportRow], db: Session = Depends(get_db)):
    """Import lead rows submitted from the manual bulk-entry form."""
    if not rows:
        raise HTTPException(status_code=400, detail="Provide at least one lead row.")
    if len(rows) > 1000:
        raise HTTPException(status_code=400, detail="A maximum of 1,000 rows can be imported at once.")
    return _import_leads(rows, db)


@router.post("/import/csv", response_model=ImportSummary)
async def import_csv_leads(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import lead rows from a UTF-8 CSV file with a company_name column."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a CSV file.")

    try:
        content = (await file.read()).decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="The CSV must be UTF-8 encoded.") from exc

    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames or "company_name" not in reader.fieldnames:
        raise HTTPException(status_code=400, detail="The CSV must include a company_name column.")

    parsed_rows: List[LeadImportRow] = []
    row_numbers: List[int] = []
    parse_errors: List[ImportResult] = []
    for row_number, source_row in enumerate(reader, start=2):
        if not any(_optional_text(value) for value in source_row.values()):
            continue
        try:
            tech_stack = source_row.get("tech_stack")
            if tech_stack:
                source_row["tech_stack"] = [item.strip() for item in tech_stack.split("|") if item.strip()]
            source_row["deal_value"] = _parse_deal_value(source_row.get("deal_value"))
            parsed_rows.append(LeadImportRow.model_validate(source_row))
            row_numbers.append(row_number)
        except (TypeError, ValueError) as exc:
            parse_errors.append(ImportResult(row=row_number, status="error", detail=str(exc)))

    if len(parsed_rows) + len(parse_errors) > 1000:
        raise HTTPException(status_code=400, detail="A maximum of 1,000 rows can be imported at once.")

    summary = _import_leads(parsed_rows, db, row_numbers)
    if parse_errors:
        summary.errors += len(parse_errors)
        summary.total_rows += len(parse_errors)
        summary.results.extend(parse_errors)
        summary.results.sort(key=lambda result: result.row)
    return summary


@router.get("", response_model=List[LeadOut])
def list_leads(
    q: Optional[str] = Query(None, description="Search by company, contact, or industry"),
    status: Optional[str] = Query(None, description="Filter by lead_status"),
    segment: Optional[str] = Query(None, description="Filter by segment"),
    db: Session = Depends(get_db),
):
    query = db.query(Lead)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Lead.company_name.ilike(like),
                Lead.contact_name.ilike(like),
                Lead.industry.ilike(like),
            )
        )
    if status:
        query = query.filter(Lead.lead_status == status)
    if segment:
        query = query.filter(Lead.segment == segment)

    return query.order_by(Lead.created_at.desc()).all()


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return lead


@router.put("/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(lead, field, value)
    lead.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    db.delete(lead)
    db.commit()
    return {"message": f"Lead {lead_id} deleted."}


# --------------------------------------------------------------------------
# ENGAGEMENT HISTORY (sales_interactions)
# --------------------------------------------------------------------------
@router.post("/{lead_id}/interactions", response_model=InteractionOut)
def log_interaction(lead_id: int, payload: InteractionCreate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    interaction = SalesInteraction(lead_id=lead_id, **payload.model_dump())
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@router.get("/{lead_id}/interactions", response_model=List[InteractionOut])
def list_interactions(lead_id: int, db: Session = Depends(get_db)):
    return (
        db.query(SalesInteraction)
        .filter(SalesInteraction.lead_id == lead_id)
        .order_by(SalesInteraction.interaction_date.desc())
        .all()
    )
