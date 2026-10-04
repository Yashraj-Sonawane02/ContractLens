# 🛡️ ContractLens: AI-Powered Legal Document Intelligence Platform
## Complete Developer & AI Assistant Briefing Document

---

## 📌 1. Project Overview & Objective
**ContractLens** (also referred to as *LeagLease V2*) is a privacy-first, AI-driven legal document intelligence and risk assessment platform specifically grounded in **Indian Jurisprudence** (focusing on Maharashtra Rental & Property Laws).

### The Problem It Solves:
1. **Opaque & Oppressive Terms:** Non-lawyers and tenants routinely sign Leave & License agreements containing illegal utility cutoff threats, oppressive daily penalty fines, unconstitutional court access waivers, or 100% security deposit forfeitures hidden in complex legalese.
2. **Privacy Risks:** Uploading sensitive contracts containing names, phone numbers, Aadhaar/PAN IDs, and bank account numbers to standard cloud AI models leaks Personal Identifiable Information (PII).
3. **AI Legal Hallucinations:** Generic LLMs frequently invent non-existent court cases or incorrect section numbers when analyzing contract disputes.

### The Solution:
ContractLens combines **Local Structural PII Sanitization**, **2-Stage Clause Triage**, **Statutory Retrieval-Augmented Generation (RAG)**, and **Multi-Threaded Parallel Processing** to evaluate contract risk with 100% statutory grounding, generating plain-language explanations, alternative safer clause wording, and overall **Contract Health Scores**.

---

## 🏗️ 2. High-Level Architecture & Tech Stack

```
                               ┌──────────────────────────────────────────┐
                               │            React + Vite UI               │
                               │  (Risk Heatmap, Clause Cards, Chat,      │
                               │   Contract Comparison, Legal Explorer)   │
                               └────────────────────┬─────────────────────┘
                                                    │ REST API / Axios
                                                    ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     FastAPI Backend Server                                       │
│                                                                                                  │
│   ┌─────────────────────┐       ┌──────────────────────┐       ┌─────────────────────────────┐   │
│   │   Document Parser   │ ────> │  Contextual PII      │ ────> │    Clause Segmentation      │   │
│   │ (pdfplumber, pypdf, │       │  Sanitization Engine │       │    & 2-Stage Triage         │   │
│   │   python-docx)      │       │ (Regex + Safe-List)  │       │ (Topic & Flag Classifier)   │   │
│   └─────────────────────┘       └──────────────────────┘       └──────────────┬──────────────┘   │
│                                                                               │                  │
│                                                                               ▼                  │
│   ┌─────────────────────┐       ┌──────────────────────┐       ┌─────────────────────────────┐   │
│   │ Contract Health     │ <──── │ 4-Tier Statutory     │ <──── │ Parallel RAG Analyzer       │   │
│   │ Score Engine        │       │ Risk Rules Classifier│       │ (ThreadPoolExecutor         │   │
│   │ (100 - Deductions)  │       │ (-20, -10, -4, 0)    │       │  8 Workers, <5s Execution)  │   │
│   └─────────────────────┘       └──────────────────────┘       └──────────────▲──────────────┘   │
│                                                                               │                  │
│                                                                Statutory Context Search          │
│                                                                               │                  │
│                                                        ┌──────────────────────┴──────────────┐   │
│                                                        │ Indexed Legal Knowledge Base        │   │
│                                                        │ (Maharashtra Rent Control Act 1999, │   │
│                                                        │  Transfer of Property Act 1882,      │   │
│                                                        │  Indian Contract Act 1872)          │   │
│                                                        └─────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Tech Stack Breakdown:
* **Backend:** Python 3.11, FastAPI, Uvicorn, Pydantic, SQLAlchemy / SQLite.
* **Document Processing:** `pdfplumber`, `pypdf`, `python-docx`, Regex.
* **Parallel Execution:** `concurrent.futures.ThreadPoolExecutor` (8 workers).
* **AI & RAG:** Local JSON Statutory Legal Knowledge Base (`maharashtra_rental_laws.json`) + Google GenAI SDK (`google-genai` / Gemini 1.5 & 3.6 Flash).
* **Frontend:** React 18, Vite 5, TailwindCSS / CSS Modules, Lucide-React Icons, Axios.
* **Presentation Artifacts:** `python-pptx` custom slide generator script.

---

## 🧩 3. Core Modules & Pipeline Breakdown

### Module 1: Document Ingestion & Safe Parsing (`document_parser.py`)
* Supports `.pdf`, `.docx`, and `.txt` files.
* Uses `pdfplumber` with fallback to `pypdf` to extract text and tables page-by-page.
* **Metric Safe-Listing:** Extracts monetary amounts (`₹`, `INR`), dates, percentages (`%`), and notice periods **before** PII masking so critical financial terms are never corrupted.

### Module 2: Contextual PII Sanitization Engine (`pii_masker.py`)
* Performs automated local redaction of sensitive personal data before any text leaves the system:
  * `[GOVT_ID_PAN_1]`, `[GOVT_ID_AADHAAR_1]`
  * `[PHONE_1]`, `[EMAIL_1]`
  * `[BANK_ACCOUNT_1]`, `[IFSC_CODE_1]`
  * `[PERSON_1]`, `[ADDRESS_1]`, `[ORGANIZATION_1]`
* Preserves contract integrity while ensuring complete data privacy compliance (DPDP Act 2023).

### Module 3: Clause Segmentation & 2-Stage Triage (`clause_engine.py`)
* **Boundary Detection:** Uses structural regex patterns to split legal documents into discrete clauses.
* **Topic Classification:** Categorizes clauses into topics: *Rent & License Fee*, *Security Deposit*, *Lock-in & Notice Period*, *Penalty & Interest*, *Sub-letting*, *Maintenance & Repairs*, *Dispute & Jurisdiction*.
* **Fast Triage:** Identifies trigger words (`penalty`, `forfeit`, `eviction`, `unilateral`, `cut off`) to flag clauses requiring detailed statutory RAG analysis.

### Module 4: Indexed Legal Knowledge Base (`legal_knowledge_base.py`)
* Pre-indexed JSON database (`maharashtra_rental_laws.json`) containing exact statutory sections:
  * **Maharashtra Rent Control Act, 1999 (MRCA):** Section 29 (Utility Disconnection Ban), Section 10 & 11 (Rent Increase Caps), Section 15 & 24 (Eviction Rules), Section 55 (Registration Mandate).
  * **Transfer of Property Act, 1882 (TPA):** Section 108 (Lessor/Lessee Obligations & Structural Repairs), Section 106 (Notice Periods).
  * **Indian Contract Act, 1872 (ICA):** Section 28 (Unlawful Agreements Restraining Legal Proceedings), Section 74 (Unenforceable Oppressive Penalty Stipulations).
* Provides sub-5ms local keyword & domain relevance retrieval.

### Module 5: Statutory Risk Classification & Health Scoring (`rag_engine.py` & `parallel_analyzer.py`)
* Evaluates clauses against legal rules and assigns 4 risk levels:
  * 🔴 **CRITICAL (-20 Points):** Direct statutory violation (e.g., threat to cut off water/electricity, unilateral sole arbitrator, forcible lock-out eviction, bedroom CCTV intrusion).
  * 🟠 **HIGH (-10 Points):** Oppressive daily penalties (>= ₹500/day or >12% interest p.a.), 100% deposit forfeiture during lock-in, severe notice period imbalance (3 months vs 7 days).
  * 🟡 **MEDIUM (-4 Points):** Short inspection notice, vague maintenance limits, deposit refund timeline >30 days.
  * 🟢 **LOW (0 Points):** Standard compliant covenants.
* **Contract Health Score Formula:**
  $$\text{Health Score} = \max\left(10, \, 100 - \sum \text{Deductions}\right)$$

### Module 6: Parallel Execution Engine (`parallel_analyzer.py`)
* Uses Python `ThreadPoolExecutor(max_workers=8)` to analyze all contract clauses concurrently.
* Reduces analysis time for 50+ clause agreements from **>60 seconds to <5 seconds**.

---

## ⚡ 4. How to Run the Project locally

### Prerequisites:
* Python 3.11+
* Node.js 18+ & npm

### Step-by-Step Instructions:

#### Step 1: Clone the Repository
```bash
git clone https://github.com/Yashraj-Sonawane02/ContractLens.git
cd ContractLens
```

#### Step 2: Set Up Backend
```bash
cd backend

# Create & activate virtual environment (optional but recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install python-pptx

# Run the FastAPI server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend API will run at:* `http://127.0.0.1:8000`  
*API Docs (Swagger):* `http://127.0.0.1:8000/docs`

#### Step 3: Set Up Frontend (New Terminal)
```bash
cd ContractLens/frontend

# Install node dependencies
npm install

# Start Vite development server
npm run dev
```
*Frontend UI will run at:* `http://localhost:3000`

---

## 🎓 5. Project Review II Context (Current vs Pending Tasks)

If presenting or discussing the current development status:
* ✅ **Completed Phase:** Parser, PII engine, Safe-Lister, Clause Segmenter, Local Legal KB, 4-tier Risk Classifier, Health Score Engine, Parallel ThreadPool Analyzer, REST APIs, React Frontend, and PowerPoint Slide Deck (`ContractLens_Project_Review_II.pptx`).
* ⏳ **Pending Phase (Next Review):** Empirical accuracy & recall benchmarking against annotated contract datasets, multi-jurisdiction expansion (adding Delhi/Karnataka tenancy acts), multi-lingual translation validation (Hindi/Marathi), and end-to-end User Acceptance Testing (UAT).

---

## 🤖 6. Instructions for your Friend's AI Assistant

If your friend opens this project in Antigravity or any AI coding environment, they can pass this instruction to their AI:

> *"You are assisting on **ContractLens**, an AI-powered legal document intelligence platform grounded in Indian Laws (backend in FastAPI under `backend/app`, frontend in React under `frontend/src`). Please review `backend/app/main.py`, `backend/app/services/rag_engine.py`, `backend/app/services/parallel_analyzer.py`, and `frontend/src/App.jsx`. All core parsing, PII redaction, statutory RAG retrieval, and risk scoring logic are implemented. Maintain the 4-tier risk classification (-20 Critical, -10 High, -4 Medium) and local PII safe-listing rules when extending backend APIs or UI components."*
