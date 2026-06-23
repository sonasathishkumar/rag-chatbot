"""
auth.py — Secure authentication for RAG Chatbot
Uses bcrypt to hash passwords. One email = one permanent password.
"""

import json
import bcrypt
from pathlib import Path

USERS_FILE = Path(__file__).parent / "users.json"


def _load_users() -> dict:
    """Load the users dictionary from disk."""
    if not USERS_FILE.exists():
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_users(users: dict) -> None:
    """Persist the users dictionary to disk."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def user_exists(email: str) -> bool:
    """Return True if this email is already registered."""
    return email.lower().strip() in _load_users()


def register_user(email: str, password: str) -> dict:
    """
    Register a new user.
    - If the email already exists, return an error (never overwrite).
    - Otherwise hash the password with bcrypt and save.
    Returns: {'success': bool, 'message': str}
    """
    email = email.lower().strip()
    users = _load_users()

    if email in users:
        return {
            "success": False,
            "message": "This email is already registered. Please sign in with your existing password."
        }

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    users[email] = hashed.decode("utf-8")
    _save_users(users)
    return {"success": True, "message": "Account created successfully!"}


def verify_user(email: str, password: str) -> dict:
    """
    Verify login credentials.
    Returns: {'success': bool, 'message': str}
    """
    email = email.lower().strip()
    users = _load_users()

    if email not in users:
        return {
            "success": False,
            "message": "No account found with this email. Please create an account first."
        }

    stored_hash = users[email].encode("utf-8")
    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return {"success": True, "message": "Login successful!"}
    else:
        return {
            "success": False,
            "message": "Incorrect password. Please try again."
        }
