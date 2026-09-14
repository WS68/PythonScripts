#!/usr/bin/env python3
"""
RouterAI Model Fetcher

Fetches the list of models from the routerai.ru provider via the OpenAI protocol,
saves the intermediate result to models_list.json, then extracts context length
and pricing for each model and saves the final result to models_pricing.json
and models_pricing.csv.

Prices are recalculated to per 1M tokens.

Usage:
    python fetch_routerai_models.py
"""

# Source repository: https://github.com/WS68/PythonScripts

import csv
import datetime
import json

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_URL = "https://routerai.ru"
MODELS_LIST_URL = f"{BASE_URL}/api/v1/models"

MODELS_LIST_FILE = "models_list.json"
PRICING_JSON_FILE = "models_pricing.json"
PRICING_CSV_FILE = "models_pricing.csv"

REQUEST_TIMEOUT = 30  # seconds

TOKENS_PER_MILLION = 1_000_000


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def build_headers() -> dict:
    """Build the headers for the OpenAI protocol."""
    return {
        "Content-Type": "application/json",
    }


def save_json(data, filepath: str) -> None:
    """Save data to a JSON file with pretty formatting."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {filepath}")


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------
def fetch_models_list() -> list:
    """Fetch the list of models from the OpenAI-compatible endpoint."""
    headers = build_headers()
    print(f"Fetching models list from {MODELS_LIST_URL} ...")
    resp = requests.get(MODELS_LIST_URL, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    # The API returns {"data": [...]}
    models = data.get("data", data if isinstance(data, list) else [])
    print(f"Received {len(models)} models.")
    return models


# ---------------------------------------------------------------------------
# Data extraction
# ---------------------------------------------------------------------------
def normalize_to_per_1m(price, unit) -> float | None:
    """
    Normalize a price to per 1M tokens.

    The API reports prices per token (pricing_units = "token").
    If the unit already indicates per-1M, the value is used as-is.
    """
    if price is None:
        return None
    try:
        price = float(price)
    except (TypeError, ValueError):
        return None

    unit = (unit or "").lower()
    if unit in ("1m", "1m tokens", "million", "per 1m", "per_1m"):
        return price
    # Default assumption: per token
    return price * TOKENS_PER_MILLION


def format_created_date(created) -> str | None:
    """Convert a Unix timestamp to a readable YYYY-MM-DD date."""
    if created is None:
        return None
    try:
        return datetime.datetime.fromtimestamp(
            int(created), tz=datetime.timezone.utc
        ).strftime("%Y-%m-%d")
    except (TypeError, ValueError, OSError):
        return None


def extract_pricing_info(model: dict) -> dict | None:
    """
    Extract context length, creation date and pricing from a single model record.

    Expected model shape (from /api/v1/models):
    {
      "id": "qwen/qwen3.7-flash",
      "created": 1785190561,
      "context_length": 1000000,
      "pricing": {"prompt": 3.28e-06, "completion": 1.42e-05},
      "pricing_units": {"prompt": "token", "completion": "token"}
    }
    """
    model_id = model.get("id", "")
    if not model_id:
        return None

    pricing = model.get("pricing", {}) or {}
    pricing_units = model.get("pricing_units", {}) or {}

    input_per_1m = normalize_to_per_1m(
        pricing.get("prompt"), pricing_units.get("prompt")
    )
    output_per_1m = normalize_to_per_1m(
        pricing.get("completion"), pricing_units.get("completion")
    )

    return {
        "provider": model_id.split("/", 1)[0] if "/" in model_id else "",
        "model": model_id,
        "created": format_created_date(model.get("created")),
        "context_length": model.get("context_length"),
        "pricing": {
            "input_per_1m_tokens": input_per_1m,
            "output_per_1m_tokens": output_per_1m,
        },
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def save_pricing_csv(records: list, filepath: str) -> None:
    """Save the final pricing records to a CSV file.

    Records where any of context_length, input_per_1m_tokens or
    output_per_1m_tokens is empty are skipped.
    """
    fieldnames = [
        "provider",
        "model",
        "created",
        "context_length",
        "input_per_1m_tokens",
        "output_per_1m_tokens",
    ]
    skipped = 0
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            context_length = record.get("context_length")
            input_per_1m = record.get("pricing", {}).get("input_per_1m_tokens")
            output_per_1m = record.get("pricing", {}).get("output_per_1m_tokens")

            # Skip records with any missing value among the three key fields.
            if (
                context_length in (None, "")
                or input_per_1m in (None, "")
                or output_per_1m in (None, "")
            ):
                skipped += 1
                continue

            writer.writerow(
                {
                    "provider": record.get("provider", ""),
                    "model": record.get("model", ""),
                    "created": record.get("created", ""),
                    "context_length": context_length,
                    "input_per_1m_tokens": input_per_1m,
                    "output_per_1m_tokens": output_per_1m,
                }
            )
    print(f"Saved: {filepath} ({skipped} records skipped due to missing values)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    # Step 1: fetch the models list and save the intermediate result.
    models = fetch_models_list()
    save_json(models, MODELS_LIST_FILE)

    # Step 2: extract context length and pricing for each model.
    results = []
    for model in models:
        info = extract_pricing_info(model)
        if info is None:
            continue
        results.append(info)

    # Step 3: save the final results.
    save_json(results, PRICING_JSON_FILE)
    save_pricing_csv(results, PRICING_CSV_FILE)

    print(f"\nDone. Processed {len(results)}/{len(models)} models.")
    print(f"Intermediate result: {MODELS_LIST_FILE}")
    print(f"Final JSON:          {PRICING_JSON_FILE}")
    print(f"Final CSV:           {PRICING_CSV_FILE}")


if __name__ == "__main__":
    main()