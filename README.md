# 🧾 Receipt Scanner API — AI-Powered Expense Tracker

> Scan any receipt image and instantly get structured expense data — powered by Azure Computer Vision OCR and Groq LLaMA-3.

---

## 📌 Overview

Receipt Scanner is a FastAPI backend that turns receipt images into structured JSON expense data using a two-step AI pipeline:

1. **Azure Computer Vision** — extracts raw text from receipt images (OCR)
2. **Groq LLaMA-3.1-8B** — parses the raw text into structured expense data

Supports receipts in **English, Arabic, and French** with automatic currency detection and expense categorization. All expenses are stored in a local SQLite database.

---

## ✨ Features

- 📸 **Receipt Scanning** — upload any receipt image (JPG, PNG) and get structured data back
- 🤖 **Two-Step AI Pipeline** — Azure CV for OCR + Groq LLaMA for intelligent parsing
- 🌍 **Multilingual** — handles English, Arabic, and French receipts
- 💰 **Multi-Currency** — auto-detects USD, EUR, GBP, EGP, SAR, AED, INR, JPY, TRY
- 🗂️ **Auto-Categorization** — Food & Drinks, Transport, Shopping, Bills, Health, Travel, Entertainment
- 🛒 **Line Item Extraction** — extracts individual items and prices from receipts
- 📊 **Expense Management** — full CRUD for stored expenses
- 🗄️ **SQLite Storage** — lightweight local database via SQLAlchemy

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![Azure](https://img.shields.io/badge/Azure_Computer_Vision-OCR-blue?logo=microsoftazure)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1_8B-purple)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightblue?logo=sqlite)

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| OCR | Azure Computer Vision v3.2 |
| LLM Parsing | Groq LLaMA-3.1-8B-Instant |
| Database | SQLite + SQLAlchemy |
| Validation | Pydantic v2 |

---

## 🏗️ Architecture

```
Receipt Image (upload)
        ↓
Azure Computer Vision v3.2
(Read API — async polling)
        ↓
Raw OCR Text
        ↓
Groq LLaMA-3.1-8B-Instant
(Structured JSON extraction)
        ↓
{
  "merchant": "Carrefour",
  "date": "2025-03-15",
  "total": 127.50,
  "currency": "EGP",
  "category": "Shopping",
  "items": [
    {"name": "Milk", "price": 12.50},
    {"name": "Bread", "price": 8.00}
  ]
}
        ↓
SQLite Database (stored expense)
```

---

## 📁 Project Structure

```
OCR Project/
├── main.py                        # FastAPI app entry point
├── requirements.txt
├── .env.example
│
└── app/
    ├── config.py                  # Settings (env vars)
    ├── database.py                # SQLAlchemy setup
    │
    ├── models/
    │   └── expense.py             # SQLAlchemy ORM model
    │
    ├── schemas/
    │   └── expense.py             # Pydantic schemas + ScanResult
    │
    ├── services/
    │   ├── scanner.py             # Core AI pipeline (Azure CV + Groq)
    │   └── expense_service.py     # Expense CRUD logic
    │
    └── routers/
        ├── scan.py                # POST /api/v1/scan
        ├── expenses.py            # CRUD /api/v1/expenses
        └── health.py              # GET /health
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/scan` | Upload receipt image → structured JSON |
| `POST` | `/api/v1/scan/save` | Scan receipt and save to DB |
| `GET` | `/api/v1/expenses` | List all expenses |
| `GET` | `/api/v1/expenses/{id}` | Get single expense |
| `PUT` | `/api/v1/expenses/{id}` | Update expense |
| `DELETE` | `/api/v1/expenses/{id}` | Delete expense |

### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/scan" \
  -H "accept: application/json" \
  -F "file=@receipt.jpg"
```

### Example Response

```json
{
  "merchant": "Carrefour",
  "date": "2025-03-15",
  "total": 127.50,
  "currency": "EGP",
  "category": "Shopping",
  "items": [
    {"name": "Milk", "price": 12.50},
    {"name": "Bread", "price": 8.00},
    {"name": "Eggs", "price": 35.00}
  ]
}
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Azure Computer Vision resource (free tier: ~5,000 transactions/month)
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

```bash
# Clone the repo
git clone https://github.com/MohamedOsama-10/receipt-scanner-api.git
cd receipt-scanner-api

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in your keys
```

### Environment Variables

```env
# Azure Computer Vision
AZURE_CV_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_CV_KEY=your-azure-key

# Groq
GROQ_API_KEY=your-groq-key

# App
APP_NAME=Receipt Scanner API
DATABASE_URL=sqlite:///./money_tracker.db
```

### Run

```bash
uvicorn main:app --reload
```

Interactive API docs at: `http://localhost:8000/docs`

---

## 🌍 Supported Languages & Currencies

**Languages:** English, Arabic (Egyptian & Gulf), French

**Currencies:** USD ($), EUR (€), GBP (£), EGP, SAR, AED, INR, JPY, TRY

**Categories:**
- 🍔 Food & Drinks
- 🚗 Transport
- 🛍️ Shopping
- 💡 Bills & Utilities
- 🎬 Entertainment
- 🏥 Health
- ✈️ Travel
- 📦 Other

---

## 👨‍💻 Author

**Mohamed Osama** — AI Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com/in/mohamed-osama-558786285)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/MohamedOsama-10)

---

## 📄 License

This project is for portfolio and demonstration purposes.
