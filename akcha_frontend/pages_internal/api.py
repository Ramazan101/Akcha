"""Thin wrapper around the Django REST API."""
import requests
import streamlit as st


def base() -> str:
    return st.session_state.get("api_base", "http://localhost:8000")


def headers() -> dict:
    token = st.session_state.get("token")
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


# ── Auth ──────────────────────────────────────────────────────────────────────
def register(username: str, email: str, password: str, password2: str, income: float):
    try:
        r = requests.post(f"{base()}/api/auth/register/", json={
            "username": username, "email": email,
            "password": password, "password2": password2,
            "income": income
        }, timeout=8)
        return r.status_code in (200, 201), r.json()
    except Exception as e:
        return False, {"detail": str(e)}


def login(username: str, password: str):
    try:
        r = requests.post(f"{base()}/api/auth/login/", json={
            "username": username, "password": password
        }, timeout=8)
        if r.status_code == 200:
            return True, r.json()
        return False, r.json()
    except Exception as e:
        return False, {"detail": str(e)}


def get_profile():
    try:
        r = requests.get(f"{base()}/api/auth/profile/", headers=headers(), timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def update_profile(data: dict):
    try:
        r = requests.patch(f"{base()}/api/auth/profile/", json=data,
                           headers=headers(), timeout=8)
        return r.status_code == 200, r.json()
    except Exception as e:
        return False, {"detail": str(e)}


# ── Expenses ──────────────────────────────────────────────────────────────────
def get_expenses(category: str = None):
    params = {}
    if category and category != "Все":
        params["category"] = category
    try:
        r = requests.get(f"{base()}/api/expenses/", headers=headers(),
                         params=params, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def add_expense(title: str, amount: float, category: str, note: str = ""):
    try:
        r = requests.post(f"{base()}/api/expenses/", json={
            "title": title, "amount": amount,
            "category": category, "note": note
        }, headers=headers(), timeout=8)
        return r.status_code == 201, r.json()
    except Exception as e:
        return False, {"detail": str(e)}


def delete_expense(expense_id: int):
    try:
        r = requests.delete(f"{base()}/api/expenses/{expense_id}/",
                            headers=headers(), timeout=8)
        return r.status_code == 204
    except Exception:
        return False


# ── Goals ─────────────────────────────────────────────────────────────────────
def get_goals():
    try:
        r = requests.get(f"{base()}/api/goals/", headers=headers(), timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def add_goal(title: str, target_amount: float, deadline: str = None):
    payload = {"title": title, "target_amount": target_amount}
    if deadline:
        payload["deadline"] = deadline
    try:
        r = requests.post(f"{base()}/api/goals/", json=payload,
                          headers=headers(), timeout=8)
        return r.status_code == 201, r.json()
    except Exception as e:
        return False, {"detail": str(e)}


def update_goal(goal_id: int, current_amount: float):
    try:
        r = requests.patch(f"{base()}/api/goals/{goal_id}/",
                           json={"current_amount": current_amount},
                           headers=headers(), timeout=8)
        return r.status_code == 200, r.json()
    except Exception as e:
        return False, {"detail": str(e)}


def delete_goal(goal_id: int):
    try:
        r = requests.delete(f"{base()}/api/goals/{goal_id}/",
                            headers=headers(), timeout=8)
        return r.status_code == 204
    except Exception:
        return False


# ── Analytics ─────────────────────────────────────────────────────────────────
def get_stats():
    try:
        r = requests.get(f"{base()}/api/stats/", headers=headers(), timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


# ── AI ────────────────────────────────────────────────────────────────────────
def ai_chat(message: str, history: list):
    """Call the AI chat endpoint on the Django backend."""
    try:
        r = requests.post(f"{base()}/api/ai/chat/", json={
            "message": message,
            "history": history
        }, headers=headers(), timeout=30)
        if r.status_code == 200:
            return True, r.json()
        return False, r.json()
    except Exception as e:
        return False, {"detail": str(e)}


def ai_advice(income: float, expenses: dict):
    try:
        r = requests.post(f"{base()}/api/ai/advice/", json={
            "income": income,
            "expenses": expenses
        }, headers=headers(), timeout=30)
        if r.status_code == 200:
            return True, r.json()
        return False, r.json()
    except Exception as e:
        return False, {"detail": str(e)}