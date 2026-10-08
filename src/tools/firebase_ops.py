"""Tool: Firebase/Firestore read-write operations used by the agent.

update_apartment_status, get_apartment_status, and create_task are
exposed to the agent via @tool so the LLM can call them directly with
structured arguments. Writes go to a real Firestore database in a demo
Firebase project (not a client's) — see secrets/README.md for how to
provision the service account key this module needs.

Apartments are keyed by `unit_code` (e.g. "SM-012"), matching the CSV in
data/price_list.csv — this is the single identifier scheme used
throughout the app; there is no separate bare-number "apartment number".
Firestore is the live source of truth for an apartment's *current*
status (the Markdown/CSV knowledge base is static and can go stale after
a write here) — use get_apartment_status for status questions, not
search_knowledge_base.
"""

import csv
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from langchain_core.tools import tool

DEFAULT_CREDENTIALS_PATH = (
    Path(__file__).resolve().parent.parent.parent / "secrets" / "firebase-service-account.json"
)

_db = None


def _get_db():
    global _db
    if _db is not None:
        return _db

    try:
        firebase_admin.get_app()
    except ValueError:
        cred_path = os.environ.get(
            "FIREBASE_SERVICE_ACCOUNT_PATH", str(DEFAULT_CREDENTIALS_PATH)
        )
        if not Path(cred_path).exists():
            raise FileNotFoundError(
                f"Firebase service account key not found at {cred_path}. "
                "See secrets/README.md for how to create one."
            )
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    return _db


def seed_apartments_from_csv(csv_path: Path) -> int:
    """Idempotently seed Firestore `apartments` from the synthetic CSV.

    Only creates docs that don't already exist, so re-running ingest
    never clobbers a live status change made via update_apartment_status.
    Returns the number of newly created docs.
    """
    db = _get_db()
    created = 0
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            unit_code = row["unit_code"]
            doc_ref = db.collection("apartments").document(unit_code)
            if doc_ref.get().exists:
                continue
            doc_ref.set(
                {
                    "unit_code": unit_code,
                    "floor": int(row["floor"]),
                    "unit_type": row["unit_type"],
                    "size_sqm": int(row["size_sqm"]),
                    "price": int(row["price"]),
                    "status": row["status"],
                    "listing_agent": row["listing_agent"],
                    "updated_at": firestore.SERVER_TIMESTAMP,
                }
            )
            created += 1
    return created


@tool
def update_apartment_status(unit_code: str, status: str) -> str:
    """Update the status of an existing apartment/unit in Firestore.

    Fails without writing anything if unit_code doesn't exist — use
    get_apartment_status or the price list to confirm valid codes first
    (format "SM-0NN", e.g. "SM-012").

    Args:
        unit_code: The unit code, e.g. "SM-012".
        status: The new status, e.g. "Sold", "Available", or "Reserved".
    """
    db = _get_db()
    doc_ref = db.collection("apartments").document(unit_code)
    if not doc_ref.get().exists:
        return (
            f"Error: apartment '{unit_code}' does not exist in Firestore. "
            "No update made. Confirm the unit code (format 'SM-0NN') and try again."
        )
    doc_ref.set(
        {"status": status, "updated_at": firestore.SERVER_TIMESTAMP},
        merge=True,
    )
    return f"Apartment {unit_code} status updated to '{status}'."


@tool
def get_apartment_status(unit_code: str) -> str:
    """Look up an apartment/unit's CURRENT status directly from Firestore.

    Firestore is the live source of truth after any updates — prefer this
    over search_knowledge_base for "what is the status of unit X" style
    questions, since the static knowledge base can't reflect later writes.

    Args:
        unit_code: The unit code, e.g. "SM-012".
    """
    db = _get_db()
    doc = db.collection("apartments").document(unit_code).get()
    if not doc.exists:
        return f"No apartment found with code '{unit_code}'."
    data = doc.to_dict()
    return (
        f"Apartment {unit_code}: status={data.get('status')}, "
        f"unit_type={data.get('unit_type')}, price={data.get('price')}"
    )


@tool
def create_task(title: str, description: str = "", unit_code: str = "") -> str:
    """Create a follow-up task in Firestore.

    Skips creation and returns the existing task if an open task with the
    same title and unit_code already exists, so a duplicate/repeated call
    doesn't create a second copy of the same task.

    Args:
        title: Short task title, e.g. "Schedule handover walkthrough".
        description: Optional longer description.
        unit_code: Optional unit code this task relates to, e.g. "SM-012".
    """
    db = _get_db()
    existing = (
        db.collection("tasks")
        .where(filter=firestore.FieldFilter("title", "==", title))
        .where(filter=firestore.FieldFilter("unit_code", "==", unit_code))
        .where(filter=firestore.FieldFilter("status", "==", "open"))
        .limit(1)
        .stream()
    )
    for doc in existing:
        return f"Task '{title}' already exists (id: {doc.id}); skipped duplicate."

    _, doc_ref = db.collection("tasks").add(
        {
            "title": title,
            "description": description,
            "unit_code": unit_code,
            "status": "open",
            "created_at": firestore.SERVER_TIMESTAMP,
        }
    )
    return f"Task '{title}' created (id: {doc_ref.id})."
