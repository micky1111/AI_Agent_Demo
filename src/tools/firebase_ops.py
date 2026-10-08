"""Tool: Firebase/Firestore read-write operations used by the agent.

update_apartment_status and create_task are exposed to the agent via
@tool so the LLM can call them directly with structured arguments. Writes
go to a real Firestore database in a demo Firebase project (not a
client's) — see secrets/README.md for how to provision the service
account key this module needs.
"""

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


@tool
def update_apartment_status(apartment_number: str, status: str) -> str:
    """Update the status of an apartment unit in Firestore.

    Args:
        apartment_number: The apartment/unit number, e.g. "12".
        status: The new status, e.g. "Sold", "Available", or "Reserved".
    """
    db = _get_db()
    db.collection("apartments").document(str(apartment_number)).set(
        {
            "apartment_number": str(apartment_number),
            "status": status,
            "updated_at": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )
    return f"Apartment {apartment_number} status updated to '{status}'."


@tool
def create_task(title: str, description: str = "", apartment_number: str = "") -> str:
    """Create a follow-up task in Firestore.

    Args:
        title: Short task title, e.g. "Schedule handover walkthrough".
        description: Optional longer description.
        apartment_number: Optional apartment/unit number this task relates to.
    """
    db = _get_db()
    _, doc_ref = db.collection("tasks").add(
        {
            "title": title,
            "description": description,
            "apartment_number": apartment_number,
            "status": "open",
            "created_at": firestore.SERVER_TIMESTAMP,
        }
    )
    return f"Task '{title}' created (id: {doc_ref.id})."
