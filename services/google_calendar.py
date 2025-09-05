import os
import json
import requests
from fastapi import HTTPException
from services.supabase_client import save_token, get_token

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

OAUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
CALENDAR_API = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def get_google_auth_url(user_id: str):
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": user_id
    }
    url = requests.Request("GET", OAUTH_URL, params=params).prepare().url
    return url

def exchange_code_for_tokens(code: str, user_id: str):
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Erro ao obter tokens do Google")

    tokens = response.json()
    save_token(user_id, "google", tokens)
    return tokens

def refresh_token(user_id: str):
    tokens = get_token(user_id, "google")
    if not tokens or "refresh_token" not in tokens:
        raise HTTPException(status_code=401, detail="Usuário precisa autorizar novamente")

    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": tokens["refresh_token"],
        "grant_type": "refresh_token"
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Erro ao atualizar token")

    new_tokens = response.json()
    tokens.update(new_tokens)
    save_token(user_id, "google", tokens)
    return tokens

def create_event(user_id: str, summary: str, start_time: str, end_time: str):
    tokens = get_token(user_id, "google")
    if not tokens:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    access_token = tokens.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    event_data = {
        "summary": summary,
        "start": {"dateTime": start_time, "timeZone": "America/Sao_Paulo"},
        "end": {"dateTime": end_time, "timeZone": "America/Sao_Paulo"},
    }

    response = requests.post(CALENDAR_API, headers=headers, data=json.dumps(event_data))

    if response.status_code == 401:
        # Token expirado → tenta refresh
        tokens = refresh_token(user_id)
        access_token = tokens.get("access_token")
        headers["Authorization"] = f"Bearer {access_token}"
        response = requests.post(CALENDAR_API, headers=headers, data=json.dumps(event_data))

    if response.status_code not in [200, 201]:
        raise HTTPException(status_code=response.status_code, detail=f"Erro ao criar evento: {response.text}")

    return response.json()
