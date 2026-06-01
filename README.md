# Automation Engine

An end-to-end invoice processing pipeline that reads emails, parses PDF invoices, validates them against business rules, and posts to SAP — exposed as a FastAPI REST API with a React frontend.

---

## Project Overview

The system automates the full invoice-to-SAP workflow:

1. **email_reader** — connects to Gmail via IMAP and finds emails with PDF attachments
2. **pdf_parser** — extracts structured fields from the PDF using PyMuPDF and OCR fallback
3. **llm_extractor** — uses Google Gemini to clean and structure the extracted text
4. **validator** — applies 4 business rules (approved vendor, credit limit, future due date, INR/USD currency)
5. **api_caller** — POSTs the validated invoice to SAP; sends a Slack notification

A FastAPI layer wraps the engine so any command can be triggered over HTTP. A React frontend lets you type a plain-English command, see the workflow plan as node cards, and view the execution log.

---

## Architecture

```
  Gmail Inbox
       │  Step 1
       ▼
  email_reader  ──▶  pdf_parser  ──▶  llm_extractor
                         Step 2            Step 3
                                              │  Step 4
                                              ▼
                                         validator
                                              │  Step 5
                                    ┌─────────┴──────────┐
                                    ▼                    ▼
                               api_caller (SAP)     Slack notify

  ─────────────────────────────────────────────────────────────────
  FastAPI (localhost:8000)
    POST /run-workflow  →  engine.py  →  executor.py
    GET  /health        →  {status: ok, components: [...]}

  React (localhost:3000)
    CommandInput  →  WorkflowCanvas  →  ExecutionStatus
```

See [docs/architecture.txt](docs/architecture.txt) for the full ASCII diagram.

---

## Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/Saloni060410/automation-engine-training.git
cd automation-engine-training
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3. Install Python dependencies

```bash
pip install fastapi uvicorn requests google-genai python-dotenv \
            pydantic imap-tools pymupdf pytesseract pillow \
            openpyxl openai
```

### 4. Set up environment variables

Copy the example and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```
EMAIL=your-gmail@gmail.com
PASSWORD=your-gmail-app-password   # generate at myaccount.google.com/apppasswords
GEMINI_API_KEY=your-gemini-api-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SAP_ENDPOINT=https://your-sap-endpoint/invoices  # leave blank to use httpbin mock
```

### 5. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Usage

### Run the full pipeline (email → SAP → Slack)

```bash
source venv/bin/activate
python pipeline.py
```

### Start the FastAPI server

```bash
source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

Test it:

```bash
# Health check
curl http://localhost:8000/health

# Run a workflow
curl -X POST http://localhost:8000/run-workflow \
  -H "Content-Type: application/json" \
  -d '{"command": "enter invoice to SAP"}'
```

### Start the React frontend

```bash
cd frontend
npm start          # opens http://localhost:3000
```

Type any plain-English command (e.g. `read email`, `enter invoice to SAP`) and click **Run**.

### Run the interactive engine CLI

```bash
source venv/bin/activate
python engine/engine.py
```

### Run QA tests

```bash
source venv/bin/activate
python qa/run_tests.py
```

Logs are written to `logs/app.log`.

---

## Demo

> Record a 2-min Loom: type a command → workflow nodes appear → click Run → see execution log → Slack message arrives.

**Loom link:** *(add your recording link here)*

---

## Team

| Name | Component |
|---|---|
| Saloni | email_reader, pipeline, FastAPI |
| Vaishu | validator, QA test matrix |
| Saurabh | pdf_parser, llm_extractor |

---

## Project Structure

```
automation-engine-training/
├── components/
│   ├── email_reader.py       # Gmail IMAP + PDF attachment fetcher
│   ├── pdf_parser.py         # PyMuPDF + OCR invoice parser
│   ├── llm_extractor.py      # Gemini LLM structured extractor
│   ├── validator.py          # Business rule validator
│   └── api_caller.py         # HTTP POST with retry logic
├── engine/
│   ├── engine.py             # Gemini function-calling → workflow JSON
│   └── executor.py           # Workflow runner + execution logger
├── api/
│   └── main.py               # FastAPI app (POST /run-workflow, GET /health)
├── frontend/src/
│   ├── App.jsx
│   └── components/
│       ├── CommandInput.jsx
│       ├── WorkflowCanvas.jsx
│       └── ExecutionStatus.jsx
├── pipeline.py               # Full 5-step pipeline
├── qa/
│   ├── run_tests.py          # 15 QA test cases
│   └── test_matrix.xlsx      # Test results (15/15 pass)
├── logs/app.log              # Structured log output
├── docs/architecture.txt     # ASCII architecture diagram
├── prompts/invoice_extract.txt
├── test_data/                # Sample PDF invoices
├── .env.example
└── README.md
```
