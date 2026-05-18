"""
Receipt scanner — two-step pipeline:
  Step 1 — Azure Computer Vision : reads the receipt image and extracts raw text (OCR)
  Step 2 — Groq (llama3-8b)      : parses the text and returns structured JSON

Azure CV free tier: ~5,000 transactions/month (varies by region).
Groq free tier: no cost.
"""

import json
import re
import os
import time
import tempfile
from pathlib import Path
from datetime import date
from typing import Optional

import requests
from groq import Groq

from app.config import settings
from app.schemas.expense import ScanResult, LineItem


CLASSIFICATION_SYSTEM = """You are an expense classification AI.
You receive raw OCR text extracted from a receipt and must return ONLY a valid JSON object.
No markdown, no explanation, no extra text — just the JSON.

JSON fields:
- merchant: string (store/restaurant/company name) or null
- date: string in YYYY-MM-DD format, or null if not clearly present
- total: number — the FINAL amount paid. Look for "Total", "Grand Total", "Amount Due",
  "Net Total", "المجموع", "الإجمالي", "Montant total". NEVER return a subtotal.
- currency: ISO 4217 code detected from symbols or text:
  $ = USD, EUR = EUR, GBP = GBP, EGP = EGP, SAR = SAR,
  AED = AED, INR = INR, JPY = JPY, TRY = TRY — or null if unknown
- category: exactly one of:
  "Food & Drinks", "Transport", "Shopping", "Bills & Utilities",
  "Entertainment", "Health", "Travel", "Other"
- items: array of line items, each with:
  - name: string (item name)
  - price: number or null

Category guide:
- Food & Drinks    -> restaurants, cafes, groceries, supermarkets, food delivery
- Transport        -> gas stations, parking, taxi, Uber, bus, train, airline tickets
- Shopping         -> clothing, electronics, furniture, online stores, retail
- Bills & Utilities-> electricity, water, internet, phone bills, insurance
- Entertainment    -> cinema, games, sports, concerts, streaming subscriptions
- Health           -> pharmacy, hospital, clinic, lab tests, gym membership
- Travel           -> hotels, resorts, travel agencies, airport services
- Other            -> anything that doesn't fit above

Example output:
{"merchant":"Carrefour","date":"2025-03-15","total":127.50,"currency":"EGP","category":"Shopping","items":[{"name":"Milk","price":12.50},{"name":"Bread","price":8.00}]}"""


# ── Step 1: Azure Computer Vision OCR ────────────────────────────────────────

def _ocr_with_azure(image_path: str) -> str:
    endpoint = settings.AZURE_CV_ENDPOINT
    key = settings.AZURE_CV_KEY

    if not endpoint or not key:
        raise ValueError(
            "AZURE_CV_ENDPOINT and AZURE_CV_KEY must be set in your .env file.\n"
            "Create a free Computer Vision resource at: https://portal.azure.com"
        )

    endpoint = endpoint.rstrip("/")
    submit_url = f"{endpoint}/vision/v3.2/read/analyze"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/octet-stream",
    }

    with open(image_path, "rb") as f:
        image_data = f.read()

    response = requests.post(submit_url, headers=headers, data=image_data, timeout=30)
    response.raise_for_status()

    operation_url = response.headers.get("Operation-Location")
    if not operation_url:
        raise RuntimeError("Azure CV did not return an Operation-Location header.")

    poll_headers = {"Ocp-Apim-Subscription-Key": key}
    for _ in range(20):
        time.sleep(1.5)
        poll_resp = requests.get(operation_url, headers=poll_headers, timeout=30)
        poll_resp.raise_for_status()
        result = poll_resp.json()

        status = result.get("status", "")
        if status == "succeeded":
            break
        if status == "failed":
            raise RuntimeError(f"Azure CV OCR failed: {result}")
    else:
        raise TimeoutError("Azure CV OCR timed out. Please try again.")

    lines: list = []
    for read_result in result.get("analyzeResult", {}).get("readResults", []):
        for line in read_result.get("lines", []):
            lines.append(line.get("text", ""))

    return "\n".join(lines).strip()


# ── Step 2: Groq Classification ───────────────────────────────────────────────

def _classify_with_groq(ocr_text: str) -> dict:
    if not settings.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set in your .env file.\n"
            "Get a free key at: https://console.groq.com"
        )

    client = Groq(api_key=settings.GROQ_API_KEY)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.0,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": CLASSIFICATION_SYSTEM},
            {"role": "user", "content": f"Receipt OCR text:\n\n{ocr_text}"},
        ],
    )

    raw = response.choices[0].message.content.strip()
    return _extract_json(raw)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in model response: {text[:300]}")
    return json.loads(match.group())


# ── Public API ────────────────────────────────────────────────────────────────

async def scan_receipt_image(image_path: str) -> ScanResult:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    ocr_text = _ocr_with_azure(image_path)
    data = _classify_with_groq(ocr_text)

    raw_items = data.get("items", [])
    items = [
        LineItem(name=i.get("name", ""), price=i.get("price"))
        for i in raw_items if isinstance(i, dict)
    ]

    return ScanResult.model_validate({
        "merchant": data.get("merchant"),
        "date": data.get("date"),
        "total": data.get("total"),
        "currency": data.get("currency"),
        "category": data.get("category", "Other"),
        "items": items,
    })


async def scan_receipt_bytes(image_bytes: bytes, mime_type: str = "image/jpeg") -> ScanResult:
    suffix = ".jpg" if "jpeg" in mime_type else ".png"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    try:
        result = await scan_receipt_image(tmp_path)
    finally:
        os.unlink(tmp_path)

    return result
