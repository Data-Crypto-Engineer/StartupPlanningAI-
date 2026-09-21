# 🚀 Startup Planning & Organizer AI

**Tagline:** *Find real problems. Verify real demand. Discover companies. Build AI solutions people may actually pay for.*

---

## 🎯 Product Purpose

**Startup Planning & Organizer AI** is a commercial-first market research and opportunity-discovery platform designed specifically for independent AI developers and small AI startup founders.

Instead of generating generic AI ideas in a vacuum, this platform systematically uncovers:
1. **Real-world operational bottlenecks** experienced by verified enterprises, schools, utilities, NGOs, and public institutions.
2. **Empirical evidence** that the organization is actively spending money, recruiting personnel, outsourcing workflows, or issuing procurement tenders.
3. **High-leverage AI automation opportunities** that realistically streamline costly manual reporting, document extraction, and data validation workloads.
4. **Verified decision-makers** and contact evidence with a strict **Zero-Hallucination Policy**.
5. **Personalized, respectful outreach** (cold email + ≤200-char LinkedIn messages).
6. **Centralized Master Excel Tracker** synchronized directly with Google Drive.

---

## 🏗️ 5-File Architecture (Strict One-Way Dependency)

```
startup-planning-organizer/
│
├── app.py          # Streamlit UI & Interactive Multi-Page Navigation
│     ↓
├── workflow.py     # End-to-End Orchestrator, CRM State & Execution Audit
│     ↓
├── research.py     # Modular Market Search Adapters & Real Entity Signals
│     ↓
├── ai_engine.py    # Gemini API Reasoning, Anti-Hallucination & Scoring
│     ↓
├── storage.py      # Master Excel (4 Sheets) & Google Drive API Sync
│
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml.example
```

---

## ⚙️ Core Modules Breakdown

1. **`storage.py`**:
   - Manages the master workbook `Startup_Planning_Organizer_Tracker.xlsx` across 4 worksheets:
     - `Opportunities` (37 columns)
     - `Research Runs`
     - `Sources`
     - `Contacts`
   - Generates deterministic SHA-256 Opportunity IDs for automatic deduplication.
   - Synchronizes with designated Google Drive Folder (`1QJnRIqDLOpkaArrNIcpaehgYlHWOyXEG`).
   - Produces timestamped local backup files (`startup_opportunities_YYYY_MM_DD_HH_MM.xlsx`).

2. **`ai_engine.py`**:
   - Interfaces with the latest Gemini model (`gemini-3.8-flash`).
   - Enforces the **Zero-Hallucination Policy**:
     - *No source = no factual claim.*
     - *No verified email = "Email: Not publicly verified".*
     - *No verified LinkedIn = "LinkedIn: Not found".*
     - *No geographic confirmation = "International eligibility not verified".*
   - Calculates the transparent **0–100 Evidence-Based Commercial Intent Score**:
     - `+30` = Active paid job / freelance requirement
     - `+25` = Explicit technology / automation requirement
     - `+20` = Procurement / tender / RFP evidence
     - `+15` = Documented operational problem
     - `+10` = Repeated operational workload
   - Generates working app names (e.g. `TenderLens AI`, `GridReport AI`) and 10-step explainability trails.
   - Enforces the strict ≤200 character constraint on LinkedIn connection messages.

3. **`research.py`**:
   - Modular source adapters returning normalized records.
   - Grounded knowledge base of Pakistani enterprises (K-Electric, NTDC, Engro, Descon, TCF, LUMS, FFC) and Global remote organizations (Flexport, GitLab, Automattic, Coursera).
   - Dynamic domain discovery with empirical evidence ratings.

4. **`workflow.py`**:
   - Staged cost control (Discovery → Filtering → Verification → Outreach → Storage).
   - Manages approval queues, manual editing, and CRM statuses (`New`, `Contacted`, `Replied`, `Demo`, `Won`).

5. **`app.py`**:
   - Professional Streamlit interface across 7 dedicated views:
     1. Research Setup (Pakistan vs Global/Remote)
     2. Domain Discovery (Ranked sector catalog)
     3. Opportunity Discovery (Metrics & expandable cards)
     4. Opportunity Detail (10-step reasoning & outreach generation)
     5. Job Opportunities (Active hiring table)
     6. Outreach CRM (Lead status pipeline)
     7. Excel & Google Drive Tracker (Live download & sync)

---

## 📁 Google Drive Storage Configuration

This application maintains the master Excel tracker inside the user's designated Google Drive folder:

- **Configured Folder URL:** [Startup Planning & Organizer Google Drive Folder](https://drive.google.com/drive/folders/1QJnRIqDLOpkaArrNIcpaehgYlHWOyXEG?usp=sharing)
- **Folder ID:** `1QJnRIqDLOpkaArrNIcpaehgYlHWOyXEG`
- **Master Workbook:** `Startup_Planning_Organizer_Tracker.xlsx`

The application requires authenticated Google Drive API credentials configured in Streamlit secrets to perform cloud write operations. If credentials are not yet configured, the application safely saves the timestamped workbook locally and presents a direct `.xlsx` download button.

---

## 🚀 Installation & Local Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/startup-planning-organizer.git
   cd startup-planning-organizer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Secrets:**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit .streamlit/secrets.toml with your GEMINI_API_KEY
   ```

4. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

---

## 🌐 Web & Cloud Deployment

This repository is ready for deployment to **Streamlit Community Cloud** or container environments. Configure `GEMINI_API_KEY` and `GOOGLE_DRIVE_FOLDER_ID` in your deployment settings.
