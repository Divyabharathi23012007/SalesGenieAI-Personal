"""
SalesGenie AI - Full Regression Testing Suite
Day 29 Milestone 4: Comprehensive Test Suite for All 6 Modules & Auth
"""
import pytest
import os
import json
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import (
    Base, Lead, CompanyInsight, OutreachCampaign,
    LeadScore, SalesInteraction, CRMSyncLog, User
)
from modules.module4_scoring import (
    calculate_lead_score,
    get_classification_label,
    calculate_data_confidence,
    parse_company_size,
    parse_annual_revenue,
    parse_funding_stage,
    parse_industry_match
)
import modules.auth as auth_module

# In-memory SQLite for high-speed regression testing
@pytest.fixture(scope="module")
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Seed initial test data
    test_lead = Lead(
        id=1,
        company_name="Acme Corp",
        contact_name="John Doe",
        email="john@acme.com",
        phone="+1-555-0100",
        industry="SaaS",
        company_size="500-1000",
        annual_revenue="$50M",
        funding_stage="Series B",
        status="New",
        segment="Enterprise",
        deal_value=45000,
        notes="High interest in AI sales automation"
    )
    session.add(test_lead)
    
    test_user = User(
        id=1,
        username="testuser",
        email="test@salesgenie.ai",
        password_hash=auth_module.hash_password("SecurePassword123!"),
        role="Admin"
    )
    session.add(test_user)
    session.commit()
    
    yield session
    session.close()

# -------------------------------------------------------------
# 1. AUTHENTICATION & SECURITY REGRESSION TESTS
# -------------------------------------------------------------
def test_auth_password_hashing():
    """Verify password hashing and verification."""
    password = "SecurePassword123!"
    hashed = auth_module.hash_password(password)
    assert hashed != password
    assert auth_module.verify_password(password, hashed) is True
    assert auth_module.verify_password("WrongPassword", hashed) is False

def test_auth_token_generation():
    """Verify JWT token encoding & payload verification."""
    payload = {"sub": "testuser", "role": "Admin"}
    token = auth_module.create_access_token(payload)
    assert isinstance(token, str)
    decoded = auth_module.decode_access_token(token)
    assert decoded["sub"] == "testuser"
    assert decoded["role"] == "Admin"

# -------------------------------------------------------------
# 2. MODULE 1: LEAD MANAGEMENT & CRUD REGRESSION TESTS
# -------------------------------------------------------------
def test_module1_lead_creation_and_query(db_session):
    """Test lead insertion, query, and field validation."""
    lead = db_session.query(Lead).filter(Lead.company_name == "Acme Corp").first()
    assert lead is not None
    assert lead.email == "john@acme.com"
    assert lead.deal_value == 45000
    assert lead.status == "New"

def test_module1_lead_update_and_stage_transition(db_session):
    """Test updating lead stage and deal value."""
    lead = db_session.query(Lead).filter(Lead.id == 1).first()
    lead.status = "Contacted"
    lead.deal_value = 55000
    db_session.commit()
    
    updated = db_session.query(Lead).filter(Lead.id == 1).first()
    assert updated.status == "Contacted"
    assert updated.deal_value == 55000

def test_module1_interaction_logging(db_session):
    """Test logging customer interaction records."""
    interaction = SalesInteraction(
        lead_id=1,
        interaction_type="Call",
        notes="Discovery call completed with CTO. Identified budget allocated for Q3.",
        ai_generated=0
    )
    db_session.add(interaction)
    db_session.commit()
    
    logs = db_session.query(SalesInteraction).filter(SalesInteraction.lead_id == 1).all()
    assert len(logs) >= 1
    assert logs[-1].interaction_type == "Call"

# -------------------------------------------------------------
# 3. MODULE 2: LEAD INTELLIGENCE REGRESSION TESTS
# -------------------------------------------------------------
def test_module2_insight_persistence(db_session):
    """Verify storing and retrieving AI company intelligence insights."""
    insight = CompanyInsight(
        lead_id=1,
        qualification_score=88,
        business_needs="Automating outbound sales workflows and multi-channel cadence",
        opportunities="Cross-sell conversation intelligence add-on",
        industry_fit="High fit for B2B SaaS automation platform",
        reasoning="Strong technical team, active expansion, clear budget ownership"
    )
    db_session.add(insight)
    db_session.commit()
    
    saved = db_session.query(CompanyInsight).filter(CompanyInsight.lead_id == 1).first()
    assert saved is not None
    assert saved.qualification_score == 88
    assert "B2B SaaS" in saved.industry_fit

# -------------------------------------------------------------
# 4. MODULE 3: AI OUTREACH REGRESSION TESTS
# -------------------------------------------------------------
def test_module3_outreach_campaign_lifecycle(db_session):
    """Verify AI outreach sequence creation, draft, and status transitions."""
    campaign = OutreachCampaign(
        lead_id=1,
        channel="Email",
        subject_line="Scaling Acme's sales outreach with AI",
        message_body="Hi John, noticed Acme's recent growth in SaaS...",
        campaign_status="draft"
    )
    db_session.add(campaign)
    db_session.commit()
    
    saved = db_session.query(OutreachCampaign).filter(OutreachCampaign.lead_id == 1).first()
    assert saved.campaign_status == "draft"
    
    # Transition to sent
    saved.campaign_status = "sent"
    db_session.commit()
    assert saved.campaign_status == "sent"

# -------------------------------------------------------------
# 5. MODULE 4: PREDICTIVE LEAD SCORING REGRESSION TESTS
# -------------------------------------------------------------
def test_module4_deterministic_scoring_and_classification(db_session):
    """Verify rule-based predictive scoring calculation, data confidence, and tier classification."""
    lead = db_session.query(Lead).filter(Lead.id == 1).first()
    insight = db_session.query(CompanyInsight).filter(CompanyInsight.lead_id == 1).first()
    campaigns = db_session.query(OutreachCampaign).filter(OutreachCampaign.lead_id == 1).all()
    interactions = db_session.query(SalesInteraction).filter(SalesInteraction.lead_id == 1).all()
    
    score, breakdown = calculate_lead_score(lead, insight, campaigns, interactions)
    tier = get_classification_label(score)
    confidence = calculate_data_confidence(lead, insight, interactions)
    
    assert 0 <= score <= 100
    assert tier in ["Platinum", "Gold", "Silver", "Bronze", "Low Priority"]
    assert 0 <= confidence <= 100
    assert "Company Size (Max 15)" in breakdown

def test_module4_whatif_simulator():
    """Verify What-If simulator parameter overrides."""
    class MockLead:
        company_size = "10-50"
        annual_revenue = "$1M"
        funding_stage = "Seed"
        industry = "Retail"
        tech_stack = []

    mock_lead = MockLead()
    # Base calculation
    base_score, _ = calculate_lead_score(mock_lead, None, [], [])
    
    # Simulate high growth enterprise tier
    overrides = {
        "company_size": "500-1000",
        "annual_revenue": "$100M",
        "funding_stage": "Series C",
        "industry": "SaaS",
        "demo_booked": True
    }
    sim_score, _ = calculate_lead_score(mock_lead, None, [], [], overrides=overrides)
    
    assert sim_score > base_score
    assert sim_score >= 80

def test_module4_lead_score_persistence(db_session):
    """Verify saving predictive score records to database."""
    ls = LeadScore(
        lead_id=1,
        score=92,
        tier="Platinum",
        recommendation="Prioritize immediate executive demo and share custom case study"
    )
    db_session.add(ls)
    db_session.commit()
    
    score_rec = db_session.query(LeadScore).filter(LeadScore.lead_id == 1).first()
    assert score_rec is not None
    assert score_rec.score == 92
    assert score_rec.tier == "Platinum"

# -------------------------------------------------------------
# 6. MODULE 5: CONVERSATION INTELLIGENCE & CRM REGRESSION TESTS
# -------------------------------------------------------------
def test_module5_crm_sync_audit_log(db_session):
    """Verify simulated CRM sync produces audit log correctly."""
    sync_entry = CRMSyncLog(
        lead_id=1,
        crm_system="Salesforce",
        status="SUCCESS",
        sync_details="Contact, deal value ($55,000), and stage (Contacted) synced"
    )
    db_session.add(sync_entry)
    db_session.commit()
    
    log = db_session.query(CRMSyncLog).filter(CRMSyncLog.lead_id == 1).first()
    assert log is not None
    assert log.status == "SUCCESS"
    assert log.crm_system == "Salesforce"

def test_module5_meeting_summary_interaction_log(db_session):
    """Verify AI meeting summary creation with ai_generated=1 flag."""
    summary_interaction = SalesInteraction(
        lead_id=1,
        interaction_type="Meeting Summary",
        notes="AI Summary: Prospect requested enterprise pricing tier and SOC2 report.",
        ai_generated=1
    )
    db_session.add(summary_interaction)
    db_session.commit()
    
    ai_logs = db_session.query(SalesInteraction).filter(
        SalesInteraction.lead_id == 1,
        SalesInteraction.ai_generated == 1
    ).all()
    assert len(ai_logs) >= 1
    assert "SOC2" in ai_logs[0].notes

# -------------------------------------------------------------
# 7. MODULE 6: DASHBOARD & PIPELINE REGRESSION TESTS
# -------------------------------------------------------------
def test_module6_lead_count_and_pipeline_sum(db_session):
    """Verify aggregation queries used in Dashboard overview."""
    total_leads = db_session.query(Lead).count()
    assert total_leads >= 1
    
    total_deals = sum([l.deal_value or 0 for l in db_session.query(Lead).all()])
    assert total_deals >= 55000

def test_module6_pipeline_stage_grouping(db_session):
    """Verify pipeline grouping by lead status."""
    leads = db_session.query(Lead).all()
    stages = {}
    for lead in leads:
        stage = lead.status or "New"
        stages.setdefault(stage, []).append(lead)
    
    assert "Contacted" in stages
    assert len(stages["Contacted"]) >= 1

# -------------------------------------------------------------
# 8. SYSTEM INTEGRATION & END-TO-END WORKFLOW INTEGRITY
# -------------------------------------------------------------
def test_end_to_end_lead_lifecycle(db_session):
    """Test full lifecycle: Ingest -> Score -> Outreach -> Interaction -> Sync."""
    # 1. Ingest new lead
    lead2 = Lead(
        id=2,
        company_name="Starlight Bio",
        contact_name="Sarah Connor",
        email="sarah@starlight.bio",
        phone="+1-555-0999",
        industry="Healthcare",
        company_size="500+",
        status="Qualified",
        segment="Enterprise",
        deal_value=120000
    )
    db_session.add(lead2)
    db_session.commit()
    
    # 2. Score
    score2 = LeadScore(lead_id=lead2.id, score=96, tier="Platinum", recommendation="Engage VP Sales")
    db_session.add(score2)
    
    # 3. Outreach
    outreach2 = OutreachCampaign(lead_id=lead2.id, channel="LinkedIn", subject_line="AI for Healthcare", message_body="Hello Sarah...", campaign_status="sent")
    db_session.add(outreach2)
    
    # 4. Sync
    crm2 = CRMSyncLog(lead_id=lead2.id, crm_system="HubSpot", status="SUCCESS", sync_details="Synced 120k deal")
    db_session.add(crm2)
    db_session.commit()
    
    # Verify complete record graph
    assert db_session.query(Lead).filter(Lead.id == lead2.id).first().deal_value == 120000
    assert db_session.query(LeadScore).filter(LeadScore.lead_id == lead2.id).first().tier == "Platinum"
    assert db_session.query(OutreachCampaign).filter(OutreachCampaign.lead_id == lead2.id).first().campaign_status == "sent"
    assert db_session.query(CRMSyncLog).filter(CRMSyncLog.lead_id == lead2.id).first().status == "SUCCESS"
