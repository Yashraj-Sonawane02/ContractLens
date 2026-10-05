# ContractLens 📜⚖️
> **AI-Powered Legal Compliance, Risk Analysis & Contract Negotiation Platform for Maharashtra Leave & License Agreements**

[![CI Build](https://github.com/Yashraj-Sonawane02/ContractLens/actions/workflows/ci.yml/badge.svg)](https://github.com/Yashraj-Sonawane02/ContractLens/actions/workflows/ci.yml)
[![Accuracy](https://img.shields.io/badge/Statutory%20Accuracy-100%25-green.svg)](testing%20data/ContractLens_Empirical_Evaluation_Report.pdf)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)

---

## 🌟 Overview

**ContractLens** is an executive-grade AI legal assistant engineered specifically for **Maharashtra Leave & License Agreements**. It combines a deterministic statutory **RAG (Retrieval-Augmented Generation) Engine** with **Google Gemini AI** to detect illegal clauses, compute contract health scores, generate redlined negotiation counter-proposals, and answer legal queries with strict statutory citations.

It is grounded strictly in Indian and Maharashtra law:
* **Maharashtra Rent Control Act, 1999 (MRCA)**
* **Transfer of Property Act, 1882 (TPA)**
* **Indian Contract Act, 1872 (ICA)**
* **Arbitration & Conciliation Act, 1996**
* **Digital Personal Data Protection Act, 2023 (DPDP)**

---

## ✨ Key Features

- **🏆 100% Verified Empirical Accuracy**: Tested against 58 human-annotated ground-truth contract clauses across Pune & Thane agreements (**100% Precision, 100% Recall, 0 Health Score Delta**).
- **🛡️ Scope & Fake Document Guard**: Automatically rejects non-Maharashtra tenancy agreements, fake PDFs, or unrelated domain contracts.
- **⚡ Executive Top-3 Redline & Negotiation Engine**: Replaces overwhelming 50-clause lists with an actionable **Top 3 Critical Risks Summary** and generates redlined counter-proposals and ready-to-send landlord messages.
- **💬 Grounded Statutory Chatbot**: Answers queries solely from verified legal knowledge bases—refuses to hallucinate and states *"No grounded statutory answer available"* if unverified.
- **🔒 AES-256 Encrypted Storage**: Stores uploaded agreements in encrypted local object storage.
- **🗄️ PostgreSQL & SQLite Dual Support**: Works out of the box with zero setup using SQLite, or seamlessly scales to PostgreSQL.
- **🎨 Minimalist Executive UI (Light/Dark Mode)**: Gemini/ChatGPT-style hyper-clean dual-theme interface.

---

## 🚀 Quick Start Guide

### Prerequisites
* **Python 3.10+** installed
* **Node.js 18+** and `npm` installed
* **Google Gemini API Key** *(Optional for core statutory rule analysis, required for conversational chat & custom negotiation generation)*

---

### 1️⃣ Backend Setup (FastAPI)

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   * **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create your environment configuration file:
   ```bash
   cp .env.example .env
   ```

5. Open `.env` in a text editor and add your **Google Gemini API Key**:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_jwt_secret_key_here
   ```

6. Start the backend server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
   * The API server will be available at: `http://127.0.0.1:8000`
   * Interactive Swagger API docs: `http://127.0.0.1:8000/docs`

---

### 2️⃣ Frontend Setup (React + Vite)

1. Open a new terminal window and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

---

## 🧪 Running Tests & Empirical Benchmarks

### 1. Run Automated Pytest Suite
```bash
cd backend
pytest
```

### 2. Run 100% Empirical Benchmark Evaluation & Generate PDF Report
```bash
cd backend
python generate_eval_pdf.py
```
* Generates the verified PDF report at: [`testing data/ContractLens_Empirical_Evaluation_Report.pdf`](testing%20data/ContractLens_Empirical_Evaluation_Report.pdf)

---

## 📁 Repository Structure

```
ContractLens/
├── .github/workflows/          # CI/CD Pipeline (GitHub Actions)
├── backend/
│   ├── app/
│   │   ├── api/               # API Routers (Auth, Analysis, Document, Chat, Negotiation)
│   │   ├── core/              # Config, Security & Logging
│   │   ├── db/                # Database Sessions & Auto-Migrations
│   │   ├── models/            # SQLAlchemy DB Models
│   │   └── services/          # Statutory RAG, Negotiation Engine, Storage Service, PDF/DOCX Generators
│   ├── data/legal_db/         # Statutory Legal KB (MRCA 1999, TPA 1882, ICA 1872)
│   ├── tests/                 # Automated Pytest Suite
│   ├── .env.example           # Environment Template
│   ├── generate_eval_pdf.py   # Benchmark Evaluation PDF Generator
│   └── requirements.txt       # Backend Dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # Risk Dashboard, Negotiation Generator, Clause Cards, Chatbot
│   │   ├── pages/             # Landing Page, History Page
│   │   └── App.jsx
│   └── package.json           # Frontend Dependencies
└── testing data/              # Ground-Truth Datasets (Pune & Thane) + Audit Report PDF
```

---

## 📜 License & Disclaimer

**Disclaimer:** ContractLens provides AI-assisted statutory analysis for informational and legal literacy purposes under Maharashtra property law. It does not constitute formal legal representation. Users should consult a qualified legal practitioner before executing legal contracts.
