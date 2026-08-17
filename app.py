"""
app.py
Streamlit frontend for SalesGenie AI — Modules 1, 2, and 3 fully wired up.
Run with: streamlit run app.py --server.port 8502
(or via run_all.py which starts backend + frontend together)
"""

import os
import requests
import streamlit as st
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="SalesGenie AI", page_icon=":material/auto_awesome:", layout="wide", initial_sidebar_state="expanded")

# --------------------------------------------------------------------------
# DARK THEME STYLING (matches the reference screenshot)
# --------------------------------------------------------------------------
st.markdown("""
<style>
    body, .stApp {
        background:
            radial-gradient(circle at 8% 8%, rgba(45, 212, 191, 0.24), transparent 22%),
            radial-gradient(circle at 92% 7%, rgba(99, 102, 241, 0.23), transparent 23%),
            radial-gradient(circle at 85% 86%, rgba(56, 189, 248, 0.17), transparent 20%),
            linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
        color: #0f172a;
        font-family: "Segoe UI", Arial, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #172554 100%);
        border-right: 1px solid #1e3a8a;
    }
    div[data-testid="stMain"] {
        padding-top: 0.6rem;
    }
    div[data-testid="stMainBlockContainer"] {
        max-width: 1500px;
        padding: 2rem 2.5rem 3rem;
    }
    .sg-title {
        font-size: 28px; font-weight: 900; color: #f8fafc; margin-bottom: 0px;
    }
    .sg-subtitle {
        font-size: 13px; color: #bfdbfe; margin-top: 0px; margin-bottom: 24px;
    }
    .sg-nav-header {
        font-size: 11px; color: #93c5fd; letter-spacing: 1px;
        text-transform: uppercase; margin: 18px 0 6px 0;
    }
    .sg-page-title {
        font-size: 34px; font-weight: 800; color: #0f172a; margin-bottom: 4px;
    }
    .sg-page-subtitle {
        font-size: 15px; color: #475569; margin-bottom: 28px;
    }
    .sg-error-box {
        background: linear-gradient(180deg, #fff1f2 0%, #ffe4e6 100%);
        border: 1px solid #fda4af; color: #9f1239;
        padding: 16px 20px; border-radius: 10px; font-size: 15px;
    }
    .sg-success-box {
        background: linear-gradient(180deg, #ecfdf5 0%, #d1fae5 100%);
        border: 1px solid #86efac; color: #166534;
        padding: 14px 18px; border-radius: 10px; font-size: 14px;
    }
    .sg-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        border: 1px solid #cbd5e1;
        border-radius: 16px;
        padding: 20px; margin-bottom: 16px;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.08);
    }
    .sg-auth-hero {
        max-width: 680px; margin: 4vh auto 1.5rem; padding: 1.1rem 1.5rem;
        text-align: center;
    }
    .sg-auth-mark {
        width: 52px; height: 52px; margin: 0 auto 12px; border-radius: 16px;
        display: grid; place-items: center; color: white; font-size: 26px; font-weight: 900;
        background: linear-gradient(135deg, #0f766e, #2563eb);
        box-shadow: 0 14px 30px rgba(37, 99, 235, 0.24);
    }
    .sg-auth-title { font-size: 36px; font-weight: 900; color: #0f172a; margin: 0; }
    .sg-auth-copy { color: #475569; margin: 8px 0 0; }
    .sg-badge {
        display: inline-block; background: linear-gradient(180deg, #dbeafe 0%, #bfdbfe 100%);
        color: #1d4ed8; font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 999px;
        letter-spacing: 0.5px; box-shadow: 0 2px 10px rgba(59, 130, 246, 0.18);
    }
    .sg-factor { font-weight: 800; color: #0f172a; font-size: 14px; margin-bottom: 2px; }
    .sg-factor-detail { color: #475569; font-size: 13px; margin-bottom: 14px; }
    div[data-testid="stRadio"] label {
        font-size: 15px; padding: 4px 0; color: #0f172a; font-weight: 600;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] label,
    section[data-testid="stSidebar"] [data-testid="stRadio"] label *,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(191, 219, 254, 0.30);
        box-shadow: none;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.20);
        transform: none;
        box-shadow: none;
    }
    .stButton>button {
        background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%);
        color: white; border: none; border-radius: 10px;
        font-weight: 800; box-shadow: 0 10px 20px rgba(37, 99, 235, 0.22);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(180deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-1px);
        box-shadow: 0 12px 24px rgba(37, 99, 235, 0.28);
    }
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea,
    .stMultiSelect>div>div>div {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
    }
    .stTabs [role="tab"] {
        color: #334155;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [role="tab"][aria-selected="true"] {
        color: #1d4ed8;
        font-weight: 800;
        background: rgba(219, 234, 254, 0.65);
    }
    .stDataFrame {
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# API HELPERS
# --------------------------------------------------------------------------
def backend_alive() -> bool:
    try:
        r = requests.get(f"{FASTAPI_URL}/", timeout=2)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


def api_get(path, **kwargs):
    return requests.get(f"{FASTAPI_URL}{path}", headers=auth_headers(kwargs.pop("headers", None)), timeout=kwargs.pop("timeout", 10), **kwargs)


def api_post(path, **kwargs):
    return requests.post(f"{FASTAPI_URL}{path}", headers=auth_headers(kwargs.pop("headers", None)), timeout=kwargs.pop("timeout", 30), **kwargs)


def api_put(path, **kwargs):
    return requests.put(f"{FASTAPI_URL}{path}", headers=auth_headers(kwargs.pop("headers", None)), timeout=kwargs.pop("timeout", 10), **kwargs)


def api_delete(path, **kwargs):
    return requests.delete(f"{FASTAPI_URL}{path}", headers=auth_headers(kwargs.pop("headers", None)), timeout=kwargs.pop("timeout", 10), **kwargs)


def auth_headers(extra_headers=None):
    """Attach the signed backend session token to each protected API request."""
    headers = dict(extra_headers or {})
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def authenticate(path: str, payload: dict):
    try:
        response = requests.post(f"{FASTAPI_URL}{path}", json=payload, timeout=20)
        if response.status_code in (200, 201):
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.current_user = data["user"]
            st.rerun()
        return response
    except requests.exceptions.RequestException as exc:
        st.error(f"Could not reach the authentication service: {exc}")
        return None


def render_auth_screen():
    st.markdown('''<div class="sg-auth-hero"><div class="sg-auth-mark">S</div>
        <p class="sg-auth-title">Welcome to SalesGenie</p>
        <p class="sg-auth-copy">AI-Powered Intelligent Sales Forecasting Platform using Predictive Analytics</p></div>''', unsafe_allow_html=True)
    _, auth_column, _ = st.columns([1, 1.35, 1])
    with auth_column:
        login_tab, register_tab = st.tabs(["Sign in", "Create account"])
        with login_tab:
            with st.form("login_form", border=True):
                st.subheader("Sign in to your workspace")
                email = st.text_input("Work email", placeholder="you@company.com", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                submitted = st.form_submit_button("Sign in", type="primary", icon=":material/login:", width="stretch")
            if submitted:
                if not email or not password:
                    st.warning("Enter your email and password.", icon=":material/info:")
                else:
                    response = authenticate("/auth/login", {"email": email, "password": password})
                    if response is not None and response.status_code != 200:
                        st.error(safe_json(response).get("detail", "Unable to sign in."))
        with register_tab:
            with st.form("register_form", border=True):
                st.subheader("Create your secure account")
                name = st.text_input("Full name", placeholder="Alex Morgan", key="register_name")
                email = st.text_input("Work email", placeholder="alex@company.com", key="register_email")
                password = st.text_input("Password", type="password", help="Use at least 8 characters.", key="register_password")
                confirmation = st.text_input("Confirm password", type="password", key="register_confirm_password")
                submitted = st.form_submit_button("Create account", type="primary", icon=":material/person_add:", width="stretch")
            if submitted:
                if not name or not email or not password:
                    st.warning("Complete all fields to create your account.", icon=":material/info:")
                elif password != confirmation:
                    st.error("Passwords do not match.")
                elif len(password) < 8:
                    st.error("Use a password with at least 8 characters.")
                else:
                    response = authenticate("/auth/register", {"name": name, "email": email, "password": password})
                    if response is not None and response.status_code != 201:
                        st.error(safe_json(response).get("detail", "Unable to create your account."))


def safe_json(resp):
    try:
        return resp.json()
    except ValueError:
        return {"detail": resp.text.strip() or f"Empty response (HTTP {resp.status_code})"}


st.session_state.setdefault("access_token", None)
st.session_state.setdefault("current_user", None)

if not st.session_state.access_token:
    render_auth_screen()
    st.stop()

# Confirm the token on every Streamlit rerun.  This returns a user to the login
# screen when their token expires or their account has been disabled.
try:
    session_check = requests.get(
        f"{FASTAPI_URL}/auth/me",
        headers=auth_headers(),
        timeout=5,
    )
    if session_check.status_code != 200:
        st.session_state.access_token = None
        st.session_state.current_user = None
        st.rerun()
    st.session_state.current_user = session_check.json()
except requests.exceptions.RequestException:
    st.error("The authentication service is unavailable. Start the FastAPI backend and refresh this page.")
    st.stop()

def fetch_leads(q: str = None):
    params = {"q": q} if q else {}
    resp = api_get("/leads", params=params)
    resp.raise_for_status()
    return resp.json()


def lead_label(l: dict) -> str:
    seg = f" · {l['segment']}" if l.get("segment") else ""
    return f"{l['company_name']} — {l.get('contact_name') or 'No contact'}{seg}"


def fmt_money(v) -> str:
    return f"${v:,}" if v else "—"


def normalize_tech_stack(raw_value):
    if raw_value is None:
        return []

    if isinstance(raw_value, str):
        items = [part.strip() for part in raw_value.split(",") if part.strip()]
    elif isinstance(raw_value, (list, tuple, set)):
        items = [str(item).strip() for item in raw_value if str(item).strip()]
    else:
        items = [str(raw_value).strip()] if str(raw_value).strip() else []

    normalized = []
    for item in items:
        if item in TECH_STACK_OPTIONS and item not in normalized:
            normalized.append(item)
    return normalized


TECH_STACK_OPTIONS = [
    "AWS", "GCP", "Azure", "Python", "Java", "Go", "Node.js", "React",
    "Kubernetes", "Docker", "PostgreSQL", "MongoDB", "Kafka", "TensorFlow", "Terraform",
]
SEGMENTS = ["Enterprise", "Mid-Market", "Startup"]


# --------------------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sg-title">SalesGenie AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-subtitle">AI-Powered Intelligent Sales Forecasting Platform using Predictive Analytics</div>', unsafe_allow_html=True)
    st.caption(f"Signed in as {st.session_state.current_user.get('name', 'Member')}")
    if st.button("Sign out", icon=":material/logout:", key="sign_out_button", width="stretch"):
        st.session_state.access_token = None
        st.session_state.current_user = None
        st.rerun()
    st.markdown('<div class="sg-nav-header">Navigation</div>', unsafe_allow_html=True)

    page = st.radio(
        label="Navigation",
        options=[
            "Dashboard",
            "Lead Management",
            "Add Lead",
            "Lead Intelligence",
            "AI Outreach",
            "Lead Scoring",
            "Conversations",
        ],
        index=1,
        label_visibility="collapsed",
    )

if not backend_alive():
    st.markdown(
        '<div class="sg-error-box">Unable to connect to the FastAPI backend. '
        f'Make sure it is running at <b>{FASTAPI_URL}</b> '
        '(<code>uvicorn main:app --reload --port 8000</code> or run <code>python run_all.py</code>).</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# --------------------------------------------------------------------------
# MODULE 1 — LEAD MANAGEMENT
# --------------------------------------------------------------------------
def render_lead_management_v2():
    st.markdown('<div class="sg-page-title">Lead workspace</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">Search, review, update, and track every prospect in one focused workspace.</div>', unsafe_allow_html=True)
    search = st.text_input("Search leads", placeholder="Company, contact, industry, or location", key="lead_workspace_search")
    try:
        leads = fetch_leads(search or None)
    except Exception as exc:
        st.error(f"Could not load leads: {exc}")
        return
    if not leads:
        st.info("No matching leads found. Add a new prospect to get started.", icon=":material/info:")
        return

    active = sum(1 for lead in leads if lead.get("lead_status") not in {"Closed Won", "Closed Lost"})
    with st.container(horizontal=True, horizontal_alignment="distribute"):
        st.metric("Matching leads", len(leads), border=True)
        st.metric("Active pipeline", active, border=True)
        st.metric("Estimated value", fmt_money(sum(lead.get("deal_value") or 0 for lead in leads)), border=True)

    with st.container(border=True):
        st.subheader("Prospects")
        st.dataframe(
            [{"Company": lead["company_name"], "Contact": lead.get("contact_name") or "-", "Industry": lead.get("industry") or "-", "Stage": lead.get("lead_status") or "-", "Value": fmt_money(lead.get("deal_value"))} for lead in leads],
            hide_index=True, width="stretch",
        )

    label_to_lead = {lead_label(lead): lead for lead in leads}
    selected_label = st.selectbox("Open lead workspace", list(label_to_lead.keys()), key="lead_workspace_select")
    lead = label_to_lead[selected_label]
    profile_tab, edit_tab, activity_tab = st.tabs(["Profile", "Edit lead", "Activity"])

    with profile_tab:
        columns = st.columns(3, border=True)
        details = [("Company size", lead.get("company_size") or "-"), ("Annual revenue", lead.get("annual_revenue") or "-"), ("Deal value", fmt_money(lead.get("deal_value"))), ("Location", lead.get("location") or "-"), ("Funding stage", lead.get("funding_stage") or "-"), ("Pipeline stage", lead.get("lead_status") or "-")]
        for index, (label, value) in enumerate(details):
            with columns[index % len(columns)]:
                st.metric(label, value)
        tech = normalize_tech_stack(lead.get("tech_stack"))
        if tech:
            st.pills("Technology stack", tech, selection_mode="multi", default=tech, disabled=True)

    with edit_tab:
        with st.form(f"lead_workspace_edit_{lead['lead_id']}", border=True):
            left, right = st.columns(2)
            with left:
                company_name = st.text_input("Company name", value=lead["company_name"])
                contact_name = st.text_input("Contact name", value=lead.get("contact_name") or "")
                email = st.text_input("Email", value=lead.get("email") or "")
                industry = st.text_input("Industry", value=lead.get("industry") or "")
                location = st.text_input("Location", value=lead.get("location") or "")
            with right:
                company_size = st.text_input("Company size", value=lead.get("company_size") or "")
                annual_revenue = st.text_input("Annual revenue", value=lead.get("annual_revenue") or "")
                deal_value = st.number_input("Estimated deal value", min_value=0, step=5000, value=int(lead.get("deal_value") or 0))
                segment = st.selectbox("Segment", SEGMENTS, index=SEGMENTS.index(lead["segment"]) if lead.get("segment") in SEGMENTS else 0)
                stage_options = ["New", "Contacted", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
                lead_status = st.selectbox("Pipeline stage", stage_options, index=stage_options.index(lead["lead_status"]) if lead.get("lead_status") in stage_options else 0)
            tech_stack = st.multiselect("Technology stack", TECH_STACK_OPTIONS, default=normalize_tech_stack(lead.get("tech_stack")))
            save = st.form_submit_button("Save changes", type="primary", icon=":material/save:", width="stretch")
        if save:
            payload = {"company_name": company_name, "contact_name": contact_name, "email": email, "industry": industry, "location": location, "company_size": company_size, "annual_revenue": annual_revenue, "deal_value": int(deal_value) if deal_value else None, "segment": segment, "lead_status": lead_status, "tech_stack": tech_stack}
            response = api_put(f"/leads/{lead['lead_id']}", json=payload)
            if response.status_code == 200:
                st.toast("Lead updated", icon=":material/check_circle:")
                st.rerun()
            else:
                st.error(f"Update failed: {response.text}")

    with activity_tab:
        try:
            history = api_get(f"/leads/{lead['lead_id']}/interactions").json()
        except Exception:
            history = []
        with st.container(border=True):
            st.subheader("Engagement history")
            if history:
                st.dataframe([{"Type": item.get("interaction_type"), "Date": str(item.get("interaction_date", ""))[:10], "Summary": item.get("summary") or "-", "Action items": item.get("action_items") or "-"} for item in history], hide_index=True, width="stretch")
            else:
                st.caption("No interactions have been logged for this lead.")
        with st.form(f"lead_workspace_activity_{lead['lead_id']}", border=True):
            interaction_type = st.segmented_control("Interaction type", ["Call", "Email", "Meeting", "Note"], default="Call")
            summary = st.text_area("Summary")
            action_items = st.text_input("Action items")
            log = st.form_submit_button("Log interaction", icon=":material/add:", width="stretch")
        if log:
            response = api_post(f"/leads/{lead['lead_id']}/interactions", json={"interaction_type": interaction_type, "summary": summary, "action_items": action_items})
            if response.status_code == 200:
                st.rerun()
            else:
                st.error(f"Could not log interaction: {response.text}")


def render_lead_management():
    render_lead_management_v2()
    return
    st.markdown('<div class="sg-page-title">Lead Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">View, search, edit, and remove prospects.</div>', unsafe_allow_html=True)

    search = st.text_input("Search by company, contact, or industry", placeholder="e.g. TechCorp")

    try:
        leads = fetch_leads(search or None)
    except Exception as e:
        st.error(f"Could not load leads: {e}")
        return

    if not leads:
        st.info("No leads found. Add one from the 'Add Lead' page, or run seed_data.py for sample data.")
        return

    st.caption(f"{len(leads)} lead(s) found")
    table_rows = [
        {
            "Company": l["company_name"],
            "Contact": l.get("contact_name") or "—",
            "Industry": l.get("industry") or "—",
            "Segment": l.get("segment") or "—",
            "Stage": l.get("lead_status") or "—",
            "Deal Value": f"${l['deal_value']:,}" if l.get("deal_value") else "—",
            "Location": l.get("location") or "—",
        }
        for l in leads
    ]
    st.dataframe(table_rows, width="stretch", hide_index=True)

    st.markdown("---")
    st.subheader("Edit or Delete a Lead")

    label_to_lead = {lead_label(l): l for l in leads}
    selected_label = st.selectbox("Select a lead", list(label_to_lead.keys()))
    lead = label_to_lead[selected_label]

    try:
        stages_resp = api_get("/leads/stages")
        stages = stages_resp.json()["stages"] if stages_resp.status_code == 200 else \
            ["New", "Contacted", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
    except Exception:
        stages = ["New", "Contacted", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]

    with st.form(f"edit_lead_{lead['lead_id']}"):
        c1, c2 = st.columns(2)
        with c1:
            company_name = st.text_input("Company Name", value=lead["company_name"])
            contact_name = st.text_input("Contact Name", value=lead.get("contact_name") or "")
            title = st.text_input("Title", value=lead.get("title") or "")
            email = st.text_input("Email", value=lead.get("email") or "")
            phone = st.text_input("Phone", value=lead.get("phone") or "")
            industry = st.text_input("Industry", value=lead.get("industry") or "")
        with c2:
            company_size = st.text_input("Company Size", value=lead.get("company_size") or "")
            annual_revenue = st.text_input("Annual Revenue", value=lead.get("annual_revenue") or "")
            deal_value = st.number_input("Est. Deal Value ($)", min_value=0, step=5000,
                                          value=int(lead.get("deal_value") or 0))
            location = st.text_input("Location", value=lead.get("location") or "")
            funding_stage = st.text_input("Funding Stage", value=lead.get("funding_stage") or "")
            segment = st.selectbox("Segment", SEGMENTS,
                                    index=SEGMENTS.index(lead["segment"]) if lead.get("segment") in SEGMENTS else 0)
            lead_status = st.selectbox("Lead Stage", stages,
                                        index=stages.index(lead["lead_status"]) if lead.get("lead_status") in stages else 0)

        tech_stack = st.multiselect(
            "Technology Stack",
            TECH_STACK_OPTIONS,
            default=normalize_tech_stack(lead.get("tech_stack")),
        )

        col_save, col_delete = st.columns([1, 1])
        save_clicked = col_save.form_submit_button("💾 Save Changes", type="primary")
        delete_clicked = col_delete.form_submit_button("🗑️ Delete Lead")

    if save_clicked:
        payload = {
            "company_name": company_name, "contact_name": contact_name, "title": title,
            "email": email, "phone": phone, "industry": industry, "company_size": company_size,
            "annual_revenue": annual_revenue, "location": location, "funding_stage": funding_stage,
            "segment": segment, "lead_status": lead_status, "tech_stack": tech_stack,
            "deal_value": int(deal_value) if deal_value else None,
        }
        resp = api_put(f"/leads/{lead['lead_id']}", json=payload)
        if resp.status_code == 200:
            st.markdown('<div class="sg-success-box">Lead updated successfully.</div>', unsafe_allow_html=True)
            st.rerun()
        else:
            st.error(f"Update failed: {resp.text}")

    if delete_clicked:
        resp = api_delete(f"/leads/{lead['lead_id']}")
        if resp.status_code == 200:
            st.markdown('<div class="sg-success-box">Lead deleted.</div>', unsafe_allow_html=True)
            st.rerun()
        else:
            st.error(f"Delete failed: {resp.text}")

    st.markdown("---")
    st.subheader("Engagement History")
    try:
        hist = api_get(f"/leads/{lead['lead_id']}/interactions").json()
    except Exception:
        hist = []

    if hist:
        for h in hist:
            with st.expander(f"{h['interaction_type']} · {h.get('interaction_date', '')[:10]}"):
                st.write(h.get("summary") or "No summary.")
                if h.get("action_items"):
                    st.caption(f"Action items: {h['action_items']}")
    else:
        st.caption("No interactions logged yet.")

    with st.expander("➕ Log a new interaction"):
        with st.form(f"log_interaction_{lead['lead_id']}"):
            itype = st.selectbox("Type", ["Call", "Email", "Meeting", "Note"])
            summary = st.text_area("Summary")
            action_items = st.text_input("Action items (optional)")
            logged = st.form_submit_button("Log Interaction")
        if logged:
            resp = api_post(f"/leads/{lead['lead_id']}/interactions",
                             json={"interaction_type": itype, "summary": summary, "action_items": action_items})
            if resp.status_code == 200:
                st.success("Interaction logged.")
                st.rerun()
            else:
                st.error(f"Failed: {resp.text}")


# --------------------------------------------------------------------------
# MODULE 1 — ADD LEAD
# --------------------------------------------------------------------------
def render_add_lead_v2():
    st.markdown('<div class="sg-page-title">Add prospects</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">Create a detailed lead or import a prospect list in a few steps.</div>', unsafe_allow_html=True)
    single_tab, import_tab = st.tabs(["Add one lead", "Import leads"])

    with single_tab:
        with st.form("add_lead_v2_form", clear_on_submit=True, border=True):
            profile_column, business_column = st.columns(2, gap="large")
            with profile_column:
                st.markdown(":material/person: **Contact details**")
                company_name = st.text_input("Company name *")
                contact_name = st.text_input("Contact name")
                title = st.text_input("Job title")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                location = st.text_input("Location")
            with business_column:
                st.markdown(":material/domain: **Business profile**")
                industry = st.text_input("Industry")
                company_size = st.text_input("Company size", placeholder="Example: 250-500 employees")
                annual_revenue = st.text_input("Annual revenue", placeholder="Example: $45M-$60M")
                funding_stage = st.text_input("Funding stage")
                deal_value = st.number_input("Estimated deal value", min_value=0, step=5000, value=0)
                segment = st.selectbox("Segment", SEGMENTS)
            technology = st.multiselect("Technology stack", TECH_STACK_OPTIONS)
            lead_status = st.segmented_control("Starting stage", ["New", "Contacted", "Qualified"], default="New")
            submitted = st.form_submit_button("Create lead", type="primary", icon=":material/person_add:", width="stretch")
        if submitted:
            if not company_name.strip():
                st.error("Company name is required.")
            else:
                payload = {"company_name": company_name, "contact_name": contact_name, "title": title, "email": email, "phone": phone, "location": location, "industry": industry, "company_size": company_size, "annual_revenue": annual_revenue, "funding_stage": funding_stage, "deal_value": int(deal_value) if deal_value else None, "segment": segment, "lead_status": lead_status, "tech_stack": technology}
                response = api_post("/leads", json=payload)
                if response.status_code == 200:
                    st.success(f"{company_name} was added to your lead workspace.", icon=":material/check_circle:")
                else:
                    st.error(f"Could not create lead: {response.text}")

    with import_tab:
        st.caption("Upload a CSV with a required `company_name` column, or paste a simple comma-separated list.")
        csv_tab, paste_tab = st.tabs(["CSV upload", "Paste rows"])
        with csv_tab:
            with st.container(border=True):
                file = st.file_uploader("Choose CSV file", type=["csv"], key="lead_import_file")
                if st.button("Import CSV", icon=":material/upload:", type="primary", key="lead_import_csv", width="stretch"):
                    if not file:
                        st.warning("Choose a CSV file first.")
                    else:
                        response = api_post("/leads/import/csv", files={"file": (file.name, file.getvalue(), "text/csv")})
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"Created {result.get('created', 0)} lead(s).", icon=":material/check_circle:")
                        else:
                            st.error(f"Import failed: {safe_json(response).get('detail', response.text)}")
        with paste_tab:
            with st.form("lead_import_paste", border=True):
                pasted_rows = st.text_area("Rows", height=180, placeholder="Acme Corp, contact@acme.com, SaaS\nBeta Industries, , Manufacturing")
                import_rows = st.form_submit_button("Import pasted rows", icon=":material/upload:", type="primary", width="stretch")
            if import_rows:
                rows = []
                for line in pasted_rows.splitlines():
                    values = [value.strip() for value in line.split(",")]
                    if values and values[0]:
                        row = {"company_name": values[0]}
                        if len(values) > 1 and values[1]:
                            row["email"] = values[1]
                        if len(values) > 2 and values[2]:
                            row["industry"] = values[2]
                        rows.append(row)
                if not rows:
                    st.warning("Paste at least one company row.")
                else:
                    response = api_post("/leads/import/manual", json=rows)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Created {result.get('created', 0)} lead(s).", icon=":material/check_circle:")
                    else:
                        st.error(f"Import failed: {safe_json(response).get('detail', response.text)}")


def render_add_lead():
    render_add_lead_v2()
    return
    st.markdown('<div class="sg-page-title">Add Lead</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">Create a new prospect record.</div>', unsafe_allow_html=True)

    with st.form("add_lead_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            company_name = st.text_input("Company Name *")
            contact_name = st.text_input("Contact Name")
            title = st.text_input("Title")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            industry = st.text_input("Industry")
        with c2:
            company_size = st.text_input("Company Size", placeholder="e.g. 250-500 employees")
            annual_revenue = st.text_input("Annual Revenue", placeholder="e.g. $45M - $60M")
            deal_value = st.number_input("Est. Deal Value ($)", min_value=0, step=5000, value=0)
            location = st.text_input("Location")
            funding_stage = st.text_input("Funding Stage", placeholder="e.g. Series C - $28M")
            segment = st.selectbox("Segment", SEGMENTS)
            lead_status = st.selectbox("Initial Stage", ["New", "Contacted", "Qualified"])

        tech_stack = st.multiselect("Technology Stack", TECH_STACK_OPTIONS)

        submitted = st.form_submit_button("➕ Add Lead", type="primary")

    if submitted:
        if not company_name.strip():
            st.error("Company Name is required.")
            return
        payload = {
            "company_name": company_name, "contact_name": contact_name, "title": title,
            "email": email, "phone": phone, "industry": industry, "company_size": company_size,
            "annual_revenue": annual_revenue, "location": location, "funding_stage": funding_stage,
            "segment": segment, "lead_status": lead_status, "tech_stack": tech_stack,
            "deal_value": int(deal_value) if deal_value else None,
        }
        resp = api_post("/leads", json=payload)
        if resp.status_code == 200:
            st.markdown(f'<div class="sg-success-box">Lead "{company_name}" added successfully.</div>',
                        unsafe_allow_html=True)
        else:
            st.error(f"Failed to add lead: {resp.text}")

    st.markdown("---")
    st.subheader("Bulk Import")
    st.caption("Import multiple leads at once from a CSV file or a pasted grid. "
               "Rows matching an existing lead's email (or company name, if no email) are skipped as duplicates.")

    tab_csv, tab_manual = st.tabs([" CSV Upload", " Manual Bulk Entry"])

    def render_import_summary(summary: dict):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Rows", summary["total_rows"])
        c2.metric("Created", summary["created"])
        c3.metric("Duplicates Skipped", summary["duplicates"])
        c4.metric("Errors", summary["errors"])
        st.dataframe(
            [{"Row": r["row"], "Status": r["status"].capitalize(),
              "Company": r.get("company_name") or "—", "Detail": r.get("detail") or "—"}
             for r in summary["results"]],
            width="stretch", hide_index=True,
        )

    with tab_csv:
        st.caption("Required column: `company_name`. Optional: industry, contact_name, title, email, "
                   "phone, company_size, annual_revenue, location, funding_stage, lead_status, segment, "
                   "deal_value, tech_stack (separate multiple technologies with `|`).")
        csv_file = st.file_uploader("Choose a CSV file", type=["csv"], key="csv_import_uploader")
        if st.button("Import CSV", key="csv_import_btn"):
            if not csv_file:
                st.warning("Choose a CSV file first.")
            else:
                with st.spinner("Importing..."):
                    try:
                        files = {"file": (csv_file.name, csv_file.getvalue(), "text/csv")}
                        resp = api_post("/leads/import/csv", files=files)
                        if resp.status_code == 200:
                            st.markdown('<div class="sg-success-box">Import complete.</div>', unsafe_allow_html=True)
                            render_import_summary(resp.json())
                        else:
                            st.markdown(f'<div class="sg-error-box">{safe_json(resp).get("detail", resp.text)}</div>',
                                        unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="sg-error-box">Import failed: {e}</div>', unsafe_allow_html=True)

    with tab_manual:
        st.caption("One lead per line: `company_name, email, industry` (email and industry are optional).")
        manual_text = st.text_area(
            "Paste rows",
            height=140,
            placeholder="Acme Corp, sarah@acme.com, SaaS\nBeta Industries,, Manufacturing\nGamma LLC, contact@gamma.io,",
            key="manual_import_text",
        )
        if st.button("Import Rows", key="manual_import_btn"):
            lines = [ln.strip() for ln in manual_text.splitlines() if ln.strip()]
            if not lines:
                st.warning("Paste at least one row first.")
            else:
                rows = []
                for ln in lines:
                    parts = [p.strip() for p in ln.split(",")]
                    row = {"company_name": parts[0] if len(parts) > 0 else ""}
                    if len(parts) > 1 and parts[1]:
                        row["email"] = parts[1]
                    if len(parts) > 2 and parts[2]:
                        row["industry"] = parts[2]
                    rows.append(row)
                with st.spinner("Importing..."):
                    try:
                        resp = api_post("/leads/import/manual", json=rows)
                        if resp.status_code == 200:
                            st.markdown('<div class="sg-success-box">Import complete.</div>', unsafe_allow_html=True)
                            render_import_summary(resp.json())
                        else:
                            st.markdown(f'<div class="sg-error-box">{safe_json(resp).get("detail", resp.text)}</div>',
                                        unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="sg-error-box">Import failed: {e}</div>', unsafe_allow_html=True)


# --------------------------------------------------------------------------
# MODULE 2 — LEAD INTELLIGENCE
# --------------------------------------------------------------------------
def score_gauge(score: int):
    color = "#22c55e" if score >= 75 else "#eab308" if score >= 45 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"size": 48, "color": "#0f172a"}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": "#475569",
                "tickfont": {"color": "#0f172a", "size": 12},
            },
            "bar": {"color": color},
            "bgcolor": "#ffffff",
            "bordercolor": "#cbd5e1",
            "borderwidth": 1,
            "steps": [
                {"range": [0, 45], "color": "#fee2e2"},
                {"range": [45, 75], "color": "#fef3c7"},
                {"range": [75, 100], "color": "#dcfce7"},
            ],
        },
    ))
    fig.update_layout(
        height=220, margin=dict(l=20, r=20, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)", font={"color": "#0f172a"},
    )
    return fig


def render_lead_intelligence():
    st.markdown('<div class="sg-page-title">Lead Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">AI-powered company analysis and qualification scoring.</div>', unsafe_allow_html=True)

    try:
        leads = fetch_leads()
    except Exception as e:
        st.error(f"Could not load leads: {e}")
        return
    if not leads:
        st.info("No leads yet. Add one from the 'Add Lead' page first.")
        return

    label_to_lead = {lead_label(l): l for l in leads}
    selected_label = st.selectbox("Select a lead to analyze", list(label_to_lead.keys()))
    lead = label_to_lead[selected_label]

    try:
        insight_resp = api_get(f"/intelligence/{lead['lead_id']}")
        insight = insight_resp.json() if insight_resp.status_code == 200 else None
    except Exception:
        insight = None

    profile_column, action_column = st.columns([1.65, 1], gap="large")
    with profile_column:
        with st.container(border=True):
            st.subheader(lead["company_name"])
            st.caption(f"{lead.get('industry') or 'Unknown industry'} · {lead.get('segment') or 'Unsegmented'}")
            metric_one, metric_two, metric_three = st.columns(3)
            metric_one.metric("Company size", lead.get("company_size") or "—")
            metric_two.metric("Deal value", fmt_money(lead.get("deal_value")))
            metric_three.metric("Pipeline stage", lead.get("lead_status") or "—")
            st.caption(
                f"{lead.get('location') or 'Location unknown'} · "
                f"{lead.get('funding_stage') or 'Funding unknown'}"
            )
            tech_stack_display = normalize_tech_stack(lead.get("tech_stack"))
            if tech_stack_display:
                st.pills(
                    "Technology",
                    tech_stack_display,
                    selection_mode="multi",
                    default=tech_stack_display,
                    disabled=True,
                )

    with action_column:
        with st.container(border=True):
            st.badge("AI intelligence", icon=":material/auto_awesome:", color="blue")
            st.space("small")
            btn_label = "Refresh analysis" if insight else "Generate analysis"
            if st.button(btn_label, type="primary", icon=":material/auto_awesome:", width="stretch"):
                with st.spinner("Analyzing company profile..."):
                    gen_resp = api_post(f"/intelligence/generate/{lead['lead_id']}")
                    if gen_resp.status_code == 200:
                        st.rerun()
                    else:
                        st.error(f"Generation failed: {gen_resp.json().get('detail', gen_resp.text)}")
            if insight:
                st.metric("Qualification score", f"{insight['qualification_score']}/100")
                st.progress(insight["qualification_score"] / 100, text=insight["score_label"])
            else:
                st.caption("Generate a concise AI brief, fit assessment, and qualification factors.")

    if not insight:
        return

    st.space("small")
    st.subheader("Intelligence brief")
    brief_columns = st.columns(3, gap="medium")
    brief_sections = [
        ("Business needs", "target", insight.get("business_needs")),
        ("Opportunity", "trending_up", insight.get("opportunities")),
        ("Industry fit", "domain", insight.get("industry_analysis")),
    ]
    for column, (title, icon, copy) in zip(brief_columns, brief_sections):
        with column:
            with st.container(border=True, height=205):
                st.markdown(f":material/{icon}: **{title}**")
                st.write(copy or "No assessment available yet.")

    factors = insight.get("reasoning") or []
    if factors:
        st.space("small")
        st.subheader("Qualification factors")
        factor_columns = st.columns(min(3, len(factors)), gap="medium")
        for index, item in enumerate(factors):
            with factor_columns[index % len(factor_columns)]:
                with st.container(border=True):
                    st.markdown(f":material/check_circle: **{item['factor']}**")
                    st.caption(item["detail"])


# --------------------------------------------------------------------------
# MODULE 4 — LEAD SCORING & RECOMMENDATIONS
# --------------------------------------------------------------------------
def render_what_if_simulator(leads):
    st.subheader("What-if scenario builder")
    st.caption("Test engagement and company signals without changing the saved lead record.")

    label_to_lead = {lead_label(lead): lead for lead in leads}
    selected_label = st.selectbox("Choose a lead", list(label_to_lead.keys()), key="sim_lead_select")
    lead = label_to_lead[selected_label]
    lead_id = lead["lead_id"]

    with st.container(border=True):
        st.markdown(f":material/person_search: **Scenario for {lead['company_name']}**")
        context_one, context_two, context_three = st.columns(3)
        context_one.metric("Company size", lead.get("company_size") or "-")
        context_two.metric("Pipeline stage", lead.get("lead_status") or "-")
        context_three.metric("Current value", fmt_money(lead.get("deal_value")))

    with st.form("what_if_simulator_form", border=False):
        company_column, engagement_column = st.columns(2, gap="large")
        with company_column:
            with st.container(border=True):
                st.markdown(":material/domain: **Company signals**")
                comp_size = st.text_input("Company size", value=lead.get("company_size") or "")
                ann_rev = st.text_input("Annual revenue", value=lead.get("annual_revenue") or "")
                funding = st.text_input("Funding stage", value=lead.get("funding_stage") or "")
                industry = st.text_input("Industry", value=lead.get("industry") or "")
                hiring_trend = st.segmented_control("Hiring trend", ["Stable", "Growing", "Declining"], default="Stable")
                recent_news = st.segmented_control("Recent news", ["No News", "Positive News"], default="No News")
        with engagement_column:
            with st.container(border=True):
                st.markdown(":material/handshake: **Engagement signals**")
                website_eng = st.segmented_control("Website engagement", ["Low", "Medium", "High"], default="Medium")
                email_open = st.segmented_control("Email open rate", ["No Outreach", "Sent but Not Opened", "Opened"], default="No Outreach")
                email_reply = st.segmented_control("Email reply status", ["No Reply", "Replied"], default="No Reply")
                linkedin_eng = st.segmented_control("LinkedIn engagement", ["No Engagement", "Engaged"], default="No Engagement")
                demo_booked = st.toggle("Demo or meeting booked", value=False)
        run_simulation = st.form_submit_button("Run scenario", type="primary", icon=":material/play_arrow:", width="stretch")

    if not run_simulation:
        return

    payload = {
        "lead_id": lead_id, "company_size": comp_size or None, "annual_revenue": ann_rev or None,
        "funding_stage": funding or None, "industry": industry or None, "hiring_trend": hiring_trend,
        "website_engagement": website_eng, "email_open_rate": email_open, "email_reply": email_reply,
        "linkedin_engagement": linkedin_eng, "recent_news": recent_news, "demo_booked": demo_booked,
    }
    with st.spinner("Running your scenario..."):
        response = api_post("/scoring/simulate", json=payload)
    if response.status_code != 200:
        st.error(f"Simulation failed: {response.text}")
        return

    result = response.json()
    st.success("Scenario complete", icon=":material/check_circle:")
    score_column, recommendation_column = st.columns([1, 1.65], gap="large")
    with score_column:
        with st.container(border=True, height=335):
            st.badge(result["classification"], icon=":material/flag:", color="violet")
            st.metric("Simulated score", f"{result['score']}/100")
            st.progress(result["score"] / 100)
            st.caption(f"Data confidence: {result.get('confidence_score', 0)}%")
            st.plotly_chart(score_gauge(result["score"]), width="stretch", key=f"sim_gauge_{lead_id}")
    with recommendation_column:
        with st.container(border=True, height=335):
            st.markdown(":material/route: **Recommended next steps**")
            st.markdown(result.get("recommendations", "No recommendations available."))

    explanation = result.get("explanation", {})
    if explanation:
        st.subheader("Scenario score breakdown")
        factors = st.columns(min(3, len(explanation)), gap="medium")
        for index, (factor, points) in enumerate(explanation.items()):
            with factors[index % len(factors)]:
                with st.container(border=True):
                    st.markdown(f":material/tune: **{factor}**")
                    st.metric("Impact", f"{points} pts")


def render_lead_scoring():
    st.markdown('<div class="sg-page-title">Lead Scoring & Recommendations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">Rank prospects and run simulated What-If analyses.</div>', unsafe_allow_html=True)

    tab_rank, tab_score, tab_sim = st.tabs([
        " Priority Rankings",
        " Score & AI Recommendations",
        " What-If Simulator"
    ])

    with tab_rank:
        st.subheader("Lead Priority Pipeline")
        try:
            rankings = api_get("/scoring/ranking/list").json()
        except Exception as e:
            st.error(f"Could not load rankings: {e}")
            rankings = []
        
        if rankings:
            table_rows = [
                {
                    "Company": r["company_name"],
                    "Score": r["score"],
                    "Classification": r["classification"],
                    "Industry": r.get("industry") or "—",
                    "Status": r.get("lead_status") or "—",
                }
                for r in rankings
            ]
            st.dataframe(table_rows, width="stretch", hide_index=True)
        else:
            st.info("No scores available. Recalculate scoring for a lead under the 'Score & AI Recommendations' tab.")

    with tab_score:
        try:
            leads = fetch_leads()
        except Exception as e:
            st.error(f"Could not load leads: {e}")
            return
        if not leads:
            st.warning("No leads found. Add some leads first.")
            return

        label_to_lead = {lead_label(l): l for l in leads}
        selected_label = st.selectbox("Select Lead to Score", list(label_to_lead.keys()), key="score_lead_select")
        lead = label_to_lead[selected_label]
        lead_id = lead["lead_id"]

        col_profile, col_score = st.columns([1.65, 1], gap="large")

        with col_profile.container(border=True):
            st.markdown('<div class="sg-card">', unsafe_allow_html=True)
            st.markdown(f"### {lead['company_name']}")
            st.caption(f"{lead.get('industry') or 'Unknown industry'} · {lead.get('segment') or 'Unsegmented'}")
            st.write(f"**Company Size:** {lead.get('company_size') or '—'}")
            st.write(f"**Annual Revenue:** {lead.get('annual_revenue') or '—'}")
            st.write(f"**Location:** {lead.get('location') or '—'}")
            st.write(f"**Funding Stage:** {lead.get('funding_stage') or '—'}")
            tech_stack_display = normalize_tech_stack(lead.get("tech_stack"))
            if tech_stack_display:
                st.write("**Tech Stack:** " + ", ".join(tech_stack_display))
            st.write(f"**Pipeline Stage:** {lead.get('lead_status') or '—'}")
            st.write(f"**Est. Deal Value:** {fmt_money(lead.get('deal_value'))}")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_score.container(border=True):
            try:
                score_resp = api_get(f"/scoring/{lead_id}")
                score_data = score_resp.json() if score_resp.status_code == 200 else None
            except Exception:
                score_data = None

            btn_label = "🔄 Recalculate Score" if score_data else "✨ Calculate Lead Score"
            if st.button(btn_label, type="primary", key="calc_score_btn"):
                with st.spinner("Calculating score and generating recommendations..."):
                    gen_resp = api_post(f"/scoring/generate/{lead_id}")
                    if gen_resp.status_code == 200:
                        st.success("Lead score generated successfully!")
                        st.rerun()
                    else:
                        st.error(f"Generation failed: {gen_resp.text}")

            if score_data:
                st.badge(score_data["classification"], icon=":material/flag:", color="violet")
                st.metric("Lead score", f"{score_data['score']}/100")
                st.progress(score_data["score"] / 100)
                st.caption(f"Data confidence: {score_data.get('confidence_score', 0)}%")
            else:
                st.caption("Calculate the score to unlock priority factors and recommended next steps.")

        if score_data:
            st.space("small")
            recommendation_column, gauge_column = st.columns([1.65, 1], gap="large")
            with recommendation_column:
                with st.container(border=True, height=320):
                    st.subheader("Recommended next steps")
                    st.markdown(score_data.get("recommendations", "No recommendations found."))
            with gauge_column:
                with st.container(border=True, height=320):
                    st.plotly_chart(score_gauge(score_data["score"]), width="stretch", key=f"score_gauge_{lead_id}")

            explanation = score_data.get("explanation", {})
            if explanation:
                st.subheader("Score breakdown")
                factor_columns = st.columns(min(3, len(explanation)), gap="medium")
                for index, (factor, points) in enumerate(explanation.items()):
                    with factor_columns[index % len(factor_columns)]:
                        with st.container(border=True):
                            st.markdown(f":material/tune: **{factor}**")
                            st.metric("Points", f"{points} pts")

    with tab_sim:
        render_what_if_simulator(leads)
        return

        st.subheader("What-If Score Simulator")
        st.caption("Adjust the parameters below to see how they impact the lead score in real time. This will not modify the database.")
        
        sim_label_to_lead = {lead_label(l): l for l in leads}
        sim_selected_label = st.selectbox("Select Lead to Simulate", list(sim_label_to_lead.keys()), key="sim_lead_select")
        sim_lead = sim_label_to_lead[sim_selected_label]
        sim_lead_id = sim_lead["lead_id"]

        with st.form("what_if_simulator_form"):
            c1, c2 = st.columns(2)
            with c1:
                comp_size = st.text_input("Company Size", value=sim_lead.get("company_size") or "")
                ann_rev = st.text_input("Annual Revenue", value=sim_lead.get("annual_revenue") or "")
                funding = st.text_input("Funding Stage", value=sim_lead.get("funding_stage") or "")
                industry = st.text_input("Industry", value=sim_lead.get("industry") or "")
                
                hiring_trend = st.selectbox("Hiring Trend", ["Stable", "Growing", "Declining"])
                website_eng = st.selectbox("Website Engagement", ["Low", "Medium", "High"])

            with c2:
                email_open = st.selectbox("Email Open Rate", ["No Outreach", "Sent but Not Opened", "Opened"])
                email_reply = st.selectbox("Email Reply Status", ["No Reply", "Replied"])
                linkedin_eng = st.selectbox("LinkedIn Engagement", ["No Engagement", "Engaged"])
                recent_news = st.selectbox("Recent News", ["No News", "Positive News"])
                demo_booked = st.checkbox("Demo/Meeting Booked", value=False)

            run_sim = st.form_submit_button(" Run Simulation", type="primary")

        if run_sim:
            payload = {
                "lead_id": sim_lead_id,
                "company_size": comp_size or None,
                "annual_revenue": ann_rev or None,
                "funding_stage": funding or None,
                "industry": industry or None,
                "hiring_trend": hiring_trend,
                "website_engagement": website_eng,
                "email_open_rate": email_open,
                "email_reply": email_reply,
                "linkedin_engagement": linkedin_eng,
                "recent_news": recent_news,
                "demo_booked": demo_booked
            }
            with st.spinner("Simulating..."):
                sim_resp = api_post("/scoring/simulate", json=payload)
                if sim_resp.status_code == 200:
                    sim_data = sim_resp.json()
                    st.success("Simulation Complete!")
                    
                    sc1, sc2 = st.columns([1, 1])
                    with sc1:
                        st.plotly_chart(score_gauge(sim_data["score"]), width="stretch", key=f"sim_gauge_{sim_lead_id}")
                        st.markdown(f"**Simulated Classification:** `{sim_data['classification']}`")
                        st.markdown(f"**Simulated Data Confidence:** {sim_data.get('confidence_score', 0)}%")
                    with sc2:
                        st.markdown("**Simulated Scoring Explanation**")
                        for factor, points in sim_data.get("explanation", {}).items():
                            st.write(f"**{factor}:** {points} pts")
                        st.markdown("---")
                        st.markdown("**Simulated AI recommendations**")
                        st.markdown(sim_data.get("recommendations", ""))
                else:
                    st.error(f"Simulation failed: {sim_resp.text}")


# --------------------------------------------------------------------------
# MODULE 3 — AI OUTREACH GENERATION
# --------------------------------------------------------------------------
def render_outreach():
    st.markdown('<div class="sg-page-title">AI Outreach Generation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sg-page-subtitle">Generate personalized Cold Emails and Follow-up Emails using AI.</div>',
        unsafe_allow_html=True,
    )

    try:
        leads = fetch_leads()
    except Exception as e:
        st.error(f"Could not load leads: {e}")
        return
    if not leads:
        st.warning("No leads found in the database yet. Add some leads first, "
                    "or run seed_data.py to insert sample leads.")
        return

    label_to_lead = {lead_label(l): l for l in leads}

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_label = st.selectbox("Select Lead", list(label_to_lead.keys()))
        selected_lead_id = label_to_lead[selected_label]["lead_id"]
    with col2:
        email_type = st.selectbox("Email Type", ["cold_email", "follow_up"],
                                   format_func=lambda x: "Cold Email" if x == "cold_email" else "Follow-up Email")

    col3, col4 = st.columns([1, 1])
    with col3:
        tone = st.selectbox("Tone", ["professional", "friendly", "direct", "consultative"])
    with col4:
        extra_context = st.text_input("Extra context (optional)", placeholder="e.g. mention their recent funding round")

    if "generated_email" not in st.session_state:
        st.session_state.generated_email = None

    if st.button(" Generate Email", type="primary"):
        with st.spinner("Generating personalized email..."):
            try:
                payload = {
                    "lead_id": selected_lead_id, "email_type": email_type,
                    "tone": tone, "extra_context": extra_context or None,
                }
                resp = api_post("/outreach/generate", json=payload)
                if resp.status_code != 200:
                    st.error(f"Generation failed: {safe_json(resp).get('detail', resp.text)}")
                else:
                    st.session_state.generated_email = safe_json(resp)
            except requests.exceptions.Timeout:
                st.error("The AI took too long to respond (timed out after 30s). Try again.")
            except requests.exceptions.ConnectionError:
                st.error("Lost connection to the backend mid-request. Is it still running?")
            except Exception as e:
                st.error(f"Request failed: {e}")

    if st.session_state.generated_email:
        st.markdown("---")
        st.subheader("Generated Email")
        subject = st.text_input("Subject", value=st.session_state.generated_email["subject"])
        body = st.text_area("Body", value=st.session_state.generated_email["body"], height=220)

        c1, c2 = st.columns(2)
        with c1:
            if st.button(" Save as Draft"):
                _save_campaign(selected_lead_id, email_type, tone, subject, body, "draft")
        with c2:
            if st.button(" Save & Mark Sent"):
                _save_campaign(selected_lead_id, email_type, tone, subject, body, "sent")

    st.markdown("---")
    st.subheader("Outreach History for this Lead")
    try:
        history = api_get(f"/outreach/history/{selected_lead_id}").json()
    except Exception:
        history = []

    if not history:
        st.caption("No outreach sent to this lead yet.")
    else:
        for c in history:
            status_emoji = "✅" if c["campaign_status"] == "sent" else "📝"
            with st.expander(f"{status_emoji} {c['email_subject']}  ·  {c['email_type']}  ·  {c['campaign_status']}"):
                st.write(c["email_content"])


def _save_campaign(lead_id, email_type, tone, subject, body, status):
    try:
        payload = {
            "lead_id": lead_id, "email_type": email_type, "tone": tone,
            "subject": subject, "body": body, "status": status,
        }
        resp = api_post("/outreach/save", json=payload)
        if resp.status_code == 200:
            st.markdown(f'<div class="sg-success-box">Saved as {status}.</div>', unsafe_allow_html=True)
        else:
            st.error(f"Save failed: {resp.text}")
    except Exception as e:
        st.error(f"Save failed: {e}")


# --------------------------------------------------------------------------
# MODULE 6 — DASHBOARD & SALES ANALYTICS
# --------------------------------------------------------------------------
PRIORITY_COLORS = {"High": "#7f1d3a", "Medium": "#7a5b12", "Low": "#1e3a5f"}
PRIORITY_TEXT = {"High": "#fca5a5", "Medium": "#fcd34d", "Low": "#7dd3fc"}
CLASS_COLORS = {
    "Platinum": ("#3a2f6b", "#c4b5fd"),
    "Gold": ("#7a5b12", "#fcd34d"),
    "Silver": ("#3a3f4b", "#d1d5db"),
    "Bronze": ("#5c3a1e", "#fdba74"),
    "Low Priority": ("#262730", "#9ca3af"),
}


def badge(text: str, bg: str, fg: str) -> str:
    return (f'<span style="display:inline-block;background-color:{bg};color:{fg};'
            f'font-size:11px;font-weight:700;padding:3px 10px;border-radius:12px;'
            f'letter-spacing:0.5px;">{text}</span>')


def render_dashboard_v2():
    """Executive dashboard with a single visual hierarchy and no cramped board."""
    st.markdown('<div class="sg-page-title">Sales overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">A clear view of pipeline health, lead quality, and the actions that need attention.</div>', unsafe_allow_html=True)

    try:
        overview = api_get("/dashboard/overview").json()
        pipeline = api_get("/dashboard/pipeline").json()
        followups = api_get("/dashboard/followups").json()
    except Exception as exc:
        st.error(f"Could not load the dashboard: {exc}")
        return

    with st.container(horizontal=True, horizontal_alignment="distribute"):
        st.metric("Open pipeline", fmt_money(overview["pipeline_value"]), border=True)
        st.metric("Total leads", overview["total_leads"], border=True)
        st.metric("Conversion rate", f"{overview['conversion_rate']}%", border=True)
        st.metric("Average lead score", overview["avg_lead_score"] if overview["avg_lead_score"] is not None else "-", border=True)

    with st.container(horizontal=True, horizontal_alignment="distribute"):
        st.metric("Qualification score", overview["avg_qualification_score"] if overview["avg_qualification_score"] is not None else "-", border=True)
        st.metric("Campaigns sent", overview["campaigns_sent"], border=True)
        st.metric("Draft campaigns", overview["campaigns_draft"], border=True)
        st.metric("Interactions", overview["interactions_logged"], border=True)

    stages = pipeline.get("stages", [])
    columns_by_stage = pipeline.get("columns", {})
    stage_counts = [len(columns_by_stage.get(stage, [])) for stage in stages]
    stage_values = [sum(item.get("deal_value") or 0 for item in columns_by_stage.get(stage, [])) for stage in stages]
    stage_colors = ["#2563eb", "#0ea5e9", "#14b8a6", "#8b5cf6", "#f59e0b", "#10b981", "#f43f5e"]

    st.space("small")
    chart_left, chart_right = st.columns(2, gap="large")
    with chart_left:
        with st.container(border=True):
            st.subheader("Pipeline coverage")
            st.caption("Lead volume by current sales stage")
            volume_chart = go.Figure(go.Bar(
                x=stages, y=stage_counts, marker_color=stage_colors[:len(stages)],
                text=stage_counts, textposition="auto",
                hovertemplate="%{x}<br>%{y} leads<extra></extra>",
            ))
            volume_chart.update_layout(
                height=300, margin=dict(t=15, b=25, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title=None), yaxis=dict(title=None, gridcolor="#e2e8f0", dtick=1),
                showlegend=False,
            )
            st.plotly_chart(volume_chart, width="stretch", key="dashboard_v2_stage_volume")
    with chart_right:
        with st.container(border=True):
            st.subheader("Pipeline value")
            st.caption("Expected value held at each stage")
            value_chart = go.Figure(go.Bar(
                x=stage_values, y=stages, orientation="h", marker_color=stage_colors[:len(stages)],
                hovertemplate="%{y}<br>$%{x:,.0f}<extra></extra>",
            ))
            value_chart.update_layout(
                height=300, margin=dict(t=15, b=25, l=10, r=20),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title=None, tickprefix="$", tickformat=",.0s", gridcolor="#e2e8f0"),
                yaxis=dict(title=None, autorange="reversed"), showlegend=False,
            )
            st.plotly_chart(value_chart, width="stretch", key="dashboard_v2_stage_value")

    st.space("small")
    st.subheader("Pipeline by stage")
    stage_cards = st.columns(3, gap="medium", border=True)
    for index, stage in enumerate(stages):
        leads_in_stage = columns_by_stage.get(stage, [])
        with stage_cards[index % len(stage_cards)]:
            st.markdown(f":material/account_tree: **{stage}**")
            st.metric("Active leads", len(leads_in_stage))
            st.caption(f"{fmt_money(stage_values[index])} in potential value")
            if leads_in_stage:
                names = ", ".join(item["company_name"] for item in leads_in_stage[:3])
                suffix = "" if len(leads_in_stage) <= 3 else f" +{len(leads_in_stage) - 3} more"
                st.caption(names + suffix)

    st.space("small")
    st.subheader("Action queue")
    with st.container(border=True):
        if followups:
            st.caption("Prioritized recommendations generated from the latest lead activity and scores.")
            followup_rows = [
                {
                    "Priority": item.get("priority", "-"),
                    "Company": item.get("company_name", "-"),
                    "Stage": item.get("lead_status", "-"),
                    "Recommended action": item.get("reason", "-"),
                }
                for item in followups
            ]
            st.dataframe(followup_rows, hide_index=True, width="stretch")
        else:
            st.info("No follow-ups are flagged right now. Score more leads to populate this action queue.", icon=":material/check_circle:")

    with st.expander("View detailed pipeline", icon=":material/table_chart:"):
        for stage in stages:
            stage_leads = columns_by_stage.get(stage, [])
            st.markdown(f"**{stage}** · {len(stage_leads)} lead(s)")
            if stage_leads:
                st.dataframe(
                    [
                        {
                            "Company": item.get("company_name", "-"),
                            "Value": fmt_money(item.get("deal_value")),
                            "Score": item.get("score", "-"),
                            "Classification": item.get("classification", "Not scored"),
                        }
                        for item in stage_leads
                    ],
                    hide_index=True,
                    width="stretch",
                )
            else:
                st.caption("No leads in this stage.")


def render_dashboard():
    render_dashboard_v2()
    return

    st.markdown('<div class="sg-page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">Sales pipeline, conversion, and follow-up recommendations across all leads.</div>', unsafe_allow_html=True)

    try:
        overview = api_get("/dashboard/overview").json()
    except Exception as e:
        st.error(f"Could not load dashboard: {e}")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Leads", overview["total_leads"], border=True)
    c2.metric("Conversion Rate", f"{overview['conversion_rate']}%", border=True)
    c3.metric("Open Pipeline Value", fmt_money(overview["pipeline_value"]), border=True)
    c4.metric("Avg Lead Score", overview["avg_lead_score"] if overview["avg_lead_score"] is not None else "—")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Avg Qualification Score", overview["avg_qualification_score"] if overview["avg_qualification_score"] is not None else "—")
    c6.metric("Campaigns Sent", overview["campaigns_sent"], border=True)
    c7.metric("Campaigns Drafted", overview["campaigns_draft"], border=True)
    c8.metric("Interactions Logged", overview["interactions_logged"], border=True)

    st.markdown("---")
    st.subheader("Pipeline at a glance")
    try:
        pipeline = api_get("/dashboard/pipeline").json()
    except Exception as e:
        st.error(f"Could not load pipeline: {e}")
        pipeline = None

    if pipeline:
        # These summaries use the same live pipeline response as the board,
        # keeping the visuals and lead cards in sync.
        stages = pipeline["stages"]
        stage_counts = [len(pipeline["columns"][stage]) for stage in stages]
        stage_values = [sum(lead.get("deal_value") or 0 for lead in pipeline["columns"][stage]) for stage in stages]
        stage_colors = ["#60a5fa", "#38bdf8", "#2dd4bf", "#a78bfa", "#fbbf24", "#34d399", "#fb7185"]

        chart_left, chart_right = st.columns(2, gap="large", border=True)
        with chart_left:
            stage_chart = go.Figure(data=[go.Pie(
                labels=stages, values=stage_counts, hole=0.58,
                marker=dict(colors=stage_colors), textinfo="percent",
                hovertemplate="%{label}<br>%{value} leads (%{percent})<extra></extra>",
            )])
            stage_chart.update_layout(
                title="Lead distribution by stage", height=330, margin=dict(t=50, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=-0.18),
                annotations=[dict(text=f"<b>{overview['total_leads']}</b><br>leads", x=0.5, y=0.5, showarrow=False, font=dict(size=15))],
            )
            st.plotly_chart(stage_chart, width="stretch", key="dashboard_stage_distribution")

        with chart_right:
            value_chart = go.Figure(go.Bar(
                x=stage_values, y=stages, orientation="h", marker_color=stage_colors,
                hovertemplate="%{y}<br>%{x:$,.0f}<extra></extra>",
            ))
            value_chart.update_layout(
                title="Deal value by stage", height=330, margin=dict(t=50, b=10, l=10, r=20),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(tickprefix="$", tickformat=",.0s", gridcolor="#e2e8f0", title=None),
                yaxis=dict(autorange="reversed", title=None),
            )
            st.plotly_chart(value_chart, width="stretch", key="dashboard_stage_value")

        classification_counts = {}
        for stage in stages:
            for lead in pipeline["columns"][stage]:
                classification = lead.get("classification") or "Not scored"
                classification_counts[classification] = classification_counts.get(classification, 0) + 1

        if classification_counts:
            class_chart = go.Figure(go.Bar(
                x=list(classification_counts.keys()), y=list(classification_counts.values()),
                marker_color=[CLASS_COLORS.get(label, ("#64748b", ""))[0] for label in classification_counts],
                text=list(classification_counts.values()), textposition="auto",
                hovertemplate="%{x}<br>%{y} leads<extra></extra>",
            ))
            class_chart.update_layout(
                title="Lead quality mix", height=290, margin=dict(t=50, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title=None), yaxis=dict(title="Leads", gridcolor="#e2e8f0", dtick=1),
            )
            with st.container(border=True):
                st.plotly_chart(class_chart, width="stretch", key="dashboard_lead_quality")

        st.subheader("Sales pipeline")
        cols = st.columns(min(4, len(stages)), gap="medium", border=True)
        for index, stage in enumerate(pipeline["stages"]):
            leads_in_stage = pipeline["columns"][stage]
            with cols[index % len(cols)]:
                st.markdown(f"**{stage}**")
                st.caption(f"{len(leads_in_stage)} lead(s)")
                for l in leads_in_stage:
                    cls = l.get("classification")
                    bg, fg = CLASS_COLORS.get(cls, ("#262730", "#9ca3af"))
                    cls_badge = badge(cls, bg, fg) if cls else ""
                    st.markdown(
                        f'<div class="sg-card" style="padding:12px;margin-bottom:10px;">'
                        f'<div style="font-weight:700;font-size:13px;">{l["company_name"]}</div>'
                        f'<div style="color:#9ca3af;font-size:12px;margin:4px 0;">{fmt_money(l.get("deal_value"))}</div>'
                        f'{cls_badge}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

    st.markdown("---")
    st.subheader("Automated Follow-Up Recommendations")
    try:
        followups = api_get("/dashboard/followups").json()
    except Exception as e:
        st.error(f"Could not load follow-ups: {e}")
        followups = []

    if followups:
        priority_order = ["High", "Medium", "Low"]
        priority_counts = [sum(1 for item in followups if item["priority"] == priority) for priority in priority_order]
        priority_chart = go.Figure(go.Bar(
            x=priority_order, y=priority_counts,
            marker_color=[PRIORITY_COLORS[priority] for priority in priority_order],
            text=priority_counts, textposition="auto",
            hovertemplate="%{x} priority<br>%{y} recommendations<extra></extra>",
        ))
        priority_chart.update_layout(
            title="Follow-up workload by priority", height=260, margin=dict(t=50, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title=None), yaxis=dict(title="Recommendations", gridcolor="#e2e8f0", dtick=1),
        )
        with st.container(border=True):
            st.plotly_chart(priority_chart, width="stretch", key="dashboard_followup_priority")

    if not followups:
        st.info("No follow-ups flagged right now — score more leads under Lead Scoring to populate this feed.")
    for f in followups:
        bg = PRIORITY_COLORS.get(f["priority"], "#262730")
        fg = PRIORITY_TEXT.get(f["priority"], "#9ca3af")
        st.markdown(
            f'<div class="sg-card" style="display:flex;justify-content:space-between;align-items:center;">'
            f'<div>'
            f'<div style="font-weight:700;">{f["company_name"]} <span style="color:#6b7280;font-weight:400;">· {f.get("lead_status") or "—"}</span></div>'
            f'<div style="color:#9ca3af;font-size:13px;margin-top:4px;">{f["reason"]}</div>'
            f'</div>'
            f'{badge(f["priority"] + " Priority", bg, fg)}'
            f'</div>',
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------------------
# MODULE 5 — CONVERSATION INTELLIGENCE & CRM INTEGRATION
# --------------------------------------------------------------------------
def render_conversations():
    st.markdown('<div class="sg-page-title">Conversations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sg-page-subtitle">CRM sync status and AI-powered meeting/call summarization.</div>', unsafe_allow_html=True)

    try:
        leads = fetch_leads()
    except Exception as e:
        st.error(f"Could not load leads: {e}")
        return
    if not leads:
        st.warning("No leads found. Add some leads first.")
        return

    label_to_lead = {lead_label(l): l for l in leads}
    selected_label = st.selectbox("Select Lead", list(label_to_lead.keys()), key="conv_lead_select")
    lead = label_to_lead[selected_label]
    lead_id = lead["lead_id"]

    tab_crm, tab_summary, tab_activity = st.tabs([" CRM Sync Status", " Meeting Summary (AI Powered)", "📋 Recent Activity"])

    with tab_crm:
        st.markdown('<div class="sg-card">', unsafe_allow_html=True)
        st.markdown(f"**{lead['company_name']}** — sync this lead's current profile to a CRM platform.")
        st.caption("Simulated integration: no live Salesforce/HubSpot credentials are configured for this "
                   "project, so this logs the same sync record a real integration would produce.")
        platform = st.selectbox("CRM Platform", ["Salesforce", "HubSpot"], key="crm_platform_select")
        if st.button("Sync Now", key="crm_sync_btn"):
            try:
                resp = api_post(f"/conversation/sync/{lead_id}", json={"crm_platform": platform})
                if resp.status_code == 200:
                    log = resp.json()
                    st.markdown(f'<div class="sg-success-box">Synced to {log["crm_platform"]} at {log["timestamp"]}.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="sg-error-box">{safe_json(resp).get("detail", resp.text)}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="sg-error-box">Sync failed: {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("**Sync History**")
        try:
            logs = api_get(f"/conversation/sync/logs/{lead_id}").json()
        except Exception as e:
            st.error(f"Could not load sync history: {e}")
            logs = []
        if logs:
            st.dataframe(
                [{"Platform": l["crm_platform"], "Status": l["sync_status"],
                  "Detail": l.get("detail") or "—", "Timestamp": l["timestamp"]} for l in logs],
                width="stretch", hide_index=True,
            )
        else:
            st.caption("No sync history yet for this lead.")

    with tab_summary:
        st.markdown('<div class="sg-card">', unsafe_allow_html=True)
        interaction_type = st.radio("Type", ["Call", "Meeting"], horizontal=True, key="conv_type_radio")
        transcript = st.text_area(
            "Paste the call/meeting transcript",
            height=180,
            placeholder="Rep: Hi Sarah, thanks for joining...\nSarah: We're looking for better data pipeline monitoring...",
            key="conv_transcript_input",
        )
        if st.button("Generate Summary", key="conv_summarize_btn"):
            if not transcript.strip():
                st.warning("Paste a transcript first.")
            else:
                with st.spinner("Summarizing with AI..."):
                    try:
                        resp = api_post("/conversation/summarize", json={
                            "lead_id": lead_id, "transcript": transcript, "interaction_type": interaction_type,
                        })
                        if resp.status_code == 200:
                            st.session_state["last_summary"] = resp.json()
                            st.markdown('<div class="sg-success-box">Summary generated.</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="sg-error-box">{safe_json(resp).get("detail", resp.text)}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="sg-error-box">Summarization failed: {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        summary = st.session_state.get("last_summary")
        if summary and summary.get("lead_id") == lead_id:
            st.markdown('<div class="sg-card">', unsafe_allow_html=True)
            st.markdown(f'<span class="sg-badge">AI POWERED</span>', unsafe_allow_html=True)
            st.markdown(f"**{summary['interaction_type']} Summary**")
            st.write(summary.get("summary") or "—")
            st.markdown("**Action Items**")
            items = (summary.get("action_items") or "").split(" | ")
            for item in items:
                if item.strip():
                    st.markdown(f"- {item.strip()}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("**Past AI Summaries for this Lead**")
        try:
            summaries = api_get(f"/conversation/summaries/{lead_id}").json()
        except Exception as e:
            st.error(f"Could not load past summaries: {e}")
            summaries = []
        if summaries:
            for s in summaries:
                with st.expander(f"{s['interaction_type']} — {s['interaction_date']}"):
                    st.write(s.get("summary") or "—")
                    st.caption(s.get("action_items") or "No action items recorded.")
        else:
            st.caption("No AI summaries generated yet for this lead.")

    with tab_activity:
        st.markdown("**Recent CRM Sync Activity (all leads)**")
        try:
            recent = api_get("/conversation/sync/logs").json()
        except Exception as e:
            st.error(f"Could not load recent activity: {e}")
            recent = []
        if recent:
            lead_names = {l["lead_id"]: l["company_name"] for l in leads}
            st.dataframe(
                [{"Company": lead_names.get(r["lead_id"], f"Lead #{r['lead_id']}"),
                  "Platform": r["crm_platform"], "Status": r["sync_status"],
                  "Timestamp": r["timestamp"]} for r in recent],
                width="stretch", hide_index=True,
            )
        else:
            st.caption("No sync activity yet across any lead.")


# --------------------------------------------------------------------------
# ROUTER
# --------------------------------------------------------------------------
if page == "Lead Management":
    render_lead_management()
elif page == "Add Lead":
    render_add_lead()
elif page == "Lead Intelligence":
    render_lead_intelligence()
elif page == "AI Outreach":
    render_outreach()
elif page == "Lead Scoring":
    render_lead_scoring()
elif page == "Dashboard":
    render_dashboard()
elif page == "Conversations":
    render_conversations()
