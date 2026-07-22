# SalesGenie AI — All 6 Modules Complete

This build includes fully working, tested code for all six modules:
- **Module 1** — Lead Management & Prospect Database
- **Module 2** — Lead Intelligence & Company Analysis
- **Module 3** — AI Outreach Generation
- **Module 4** — Lead Scoring & Recommendation Engine
- **Module 5** — Conversation Intelligence & CRM Integration
- **Module 6** — Dashboard & Sales Analytics

Every route was tested end-to-end against a real PostgreSQL instance (create,
read, update, delete, search, engagement history, insight generation,
outreach generation/save/history, scoring, CRM sync, conversation
summarization, dashboard aggregation) before this was handed over.

## 1. Project structure

```
salesgenie/
├── .env.example
├── .gitignore
├── main.py                   # FastAPI backend — mounts all 6 module routers
├── app.py                    # Streamlit frontend — all 6 modules wired up
├── run_all.py                 # starts backend + frontend together
├── seed_data.py                # inserts 4 sample leads
├── requirements.txt
├── database/
│   ├── connection.py           # shared PostgreSQL engine/session (SQLAlchemy)
│   └── models.py               # Lead, CompanyInsight, OutreachCampaign,
│                                # LeadScore, SalesInteraction, CRMSyncLog, User
└── modules/
    ├── module1_leads.py           # ✅ CRUD + search + engagement history
    ├── module2_intelligence.py    # ✅ AI qualification scoring
    ├── module3_outreach.py        # ✅ AI cold email / follow-up generation
    ├── module4_scoring.py         # ✅ Lead scoring + AI recommendations + What-If simulator
    ├── module5_conversation.py    # ✅ CRM sync (simulated) + AI meeting/call summarization
    └── module6_dashboard.py       # ✅ KPIs, Kanban pipeline, automated follow-up feed
```

## 2. One-time setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

Edit `.env` with your own values:
```dotenv
DATABASE_URL=postgresql://postgres:<your-local-password>@localhost:5432/salesgenie
GROQ_API_KEY=gsk_...
```

`.env` is git-ignored — never commit real credentials. Each teammate keeps
their own local `.env`; only `.env.example` (placeholders) is tracked in git.

Create the database once (tables are auto-created on backend startup):
```sql
CREATE DATABASE salesgenie;
```

## 3. Run it

```bash
python seed_data.py     # only needed once, or if the leads table is empty
python run_all.py       # starts FastAPI on :8000 and Streamlit on :8502
```

http://127.0.0.1:8000/docs/ for API Endpoints

Open **http://localhost:8502**. The sidebar defaults to **Dashboard**.

## 4. What each module does

### Module 1 — Lead Management (`modules/module1_leads.py`)
- `POST /leads` · `GET /leads?q=&status=&segment=` · `GET /leads/{id}` ·
  `PUT /leads/{id}` · `DELETE /leads/{id}` · `GET /leads/stages`
- `POST /leads/{id}/interactions` / `GET /leads/{id}/interactions` — engagement history log

**Streamlit pages:** "Lead Management" (search, table, edit, delete, interaction log) and "Add Lead".

### Module 2 — Lead Intelligence (`modules/module2_intelligence.py`)
- `POST /intelligence/generate/{lead_id}` — AI qualification score (0–100), business needs, opportunities, industry fit, 3-factor reasoning
- `GET /intelligence/{lead_id}` · `GET /intelligence/{lead_id}/history`

**Streamlit page:** "Lead Intelligence" — profile card + AI panel with a qualification gauge.

### Module 3 — AI Outreach Generation (`modules/module3_outreach.py`)
- `POST /outreach/generate` — personalized cold email / follow-up
- `POST /outreach/save` · `GET /outreach/history/{lead_id}`

**Streamlit page:** "AI Outreach" — generate, edit, save as draft/sent, view history.

### Module 4 — Lead Scoring & Recommendations (`modules/module4_scoring.py`)
- `POST /scoring/generate/{lead_id}` — numeric score + classification (Platinum/Gold/Silver/Bronze) + AI recommendations
- `GET /scoring/{lead_id}` · `GET /scoring/ranking/list` · What-If simulation endpoint

**Streamlit page:** "Lead Scoring" — Priority Rankings, Score & AI Recommendations, What-If Simulator tabs.

### Module 5 — Conversation Intelligence & CRM Integration (`modules/module5_conversation.py`)
- `POST /conversation/sync/{lead_id}` — sync a lead to Salesforce/HubSpot (**simulated** — no real CRM credentials are configured, so this logs the same audit trail a real integration would, without an outbound call)
- `GET /conversation/sync/logs/{lead_id}` · `GET /conversation/sync/logs` — sync history
- `POST /conversation/summarize` — AI summary + action items from a call/meeting transcript, saved to `sales_interactions`
- `GET /conversation/summaries/{lead_id}` — past AI-generated summaries

**Streamlit page:** "Conversations" — CRM Sync Status, Meeting Summary (AI Powered), Recent Activity tabs.

### Module 6 — Dashboard & Sales Analytics (`modules/module6_dashboard.py`)
- `GET /dashboard/overview` — total leads, conversion rate, pipeline value, avg scores, campaign/interaction counts
- `GET /dashboard/pipeline` — Kanban-style breakdown by stage
- `GET /dashboard/followups` — rule-based automated follow-up recommendations (no LLM call — reads Module 4's scores + Module 1's interaction log)

**Streamlit page:** "Dashboard" — KPI cards, pipeline board, follow-up feed. This is the sidebar's default landing page.

## 5. Notes

- All six modules share one `database/models.py` / `database/connection.py` — no duplicate DB connections.
- Without a valid `GROQ_API_KEY`, Modules 2, 3, and 5's AI-generation endpoints return a clean `502`/`503` error instead of crashing — everything else (CRUD, search, history, scoring's numeric part, dashboard, CRM sync) still works, since Module 6 and the numeric half of Module 4 don't call the LLM at all.
- `Lead.deal_value` (nullable int, USD) was added in Module 6's build to power the pipeline value KPI — set it from the Add/Edit Lead form.
- `SalesInteraction.ai_generated` (0/1) distinguishes Module 5's AI summaries from Module 1's manually-logged notes in the same table.
- CRM sync is intentionally simulated: this project doesn't hold Salesforce/HubSpot OAuth credentials, so `/conversation/sync/{lead_id}` records the same kind of log entry a real sync would produce without making an outbound call. Swapping in real credentials later only requires changing the inside of `sync_lead()` in `module5_conversation.py` — the endpoint contract and DB schema don't need to change.

## 6. Troubleshooting "Unable to connect to the FastAPI backend"

- Confirm `python run_all.py` (or `uvicorn main:app --port 8000`) is running with no errors in its terminal.
- Confirm PostgreSQL is running and `DATABASE_URL` credentials are correct.
- Confirm `.env` → `FASTAPI_URL` matches the port uvicorn is bound to (default `http://127.0.0.1:8000`).
- If you see `Host not in allowlist` or similar network errors on AI-generation buttons only, that's your network blocking the Groq API — everything else in the app still works.
