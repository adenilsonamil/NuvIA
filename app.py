from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import requests
import urllib.parse

# Serviços
from services import twilio_service, openai_service, google_calendar
from db.supabase_client import save_event, get_user_tokens, save_calendar_tokens, get_or_create_user
import config

app = FastAPI()


# =========================
# Rota inicial
# =========================
@app.get("/")
def root():
    return {"message": "🤖 Secretária Pessoal Online - NuvIA"}


# =========================
# Google OAuth - iniciar fluxo
# =========================
@app.get("/google/auth")
async def google_auth():
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "response_type": "code",
        "client_id": config.GOOGLE_CLIENT_ID,
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
        "scope": "https://www.googleapis.com/auth/calendar",
        "access_type": "offline",   # Garante refresh_token
        "prompt": "consent"         # Força refresh_token na 1ª vez
    }
    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(auth_url)


# =========================
# Google OAuth - callback
# =========================
@app.get("/google/callback")
async def google_callback(request: Request):
    code = request.query_params.get("code")

    if not code:
        return {"error": "Código OAuth não recebido"}

    # Trocar code por tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    resp = requests.post(token_url, data=data)
    tokens = resp.json()

    if "access_token" not in tokens:
        return {"error": "Falha ao obter token", "details": tokens}

    # ⚠️ Aqui você deve ligar com o usuário do WhatsApp
    # Exemplo: salvar para "user_id" fixo até integrar fluxo real
    user_id = "demo_user"

    save_calendar_tokens(
        user_id=user_id,
        provider="google",
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
        client_id=config.GOOGLE_CLIENT_ID,
        client_secret=config.GOOGLE_CLIENT_SECRET,
        expires_at=tokens.get("expires_in")
    )

    return {"status": "✅ Google Calendar conectado com sucesso"}


# =========================
# Webhook do WhatsApp (Twilio)
# =========================
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.form()
    user_number = data.get("From")
    message_type = "audio" if "MediaUrl0" in data else "text"
    content = data.get("Body") if message_type == "text" else data.get("MediaUrl0")

    # Garante que usuário existe no Supabase
    user = get_or_create_user(user_number)

    # Resposta inicial
    twilio_service.send_message(user_number, "🔎 Estou analisando suas informações...")

    # 1. Transcreve áudio se necessário
    if message_type == "audio":
        text = openai_service.transcribe_audio(content)
    else:
        text = content

    # 2. Interpreta intenção
    intent = openai_service.interpret_text(text)

    # 3. Pega tokens do calendário escolhido
    tokens = get_user_tokens(user["id"], intent.get("calendar", "google"))
    if not tokens:
        twilio_service.send_message(
            user_number,
            "⚠️ Você ainda não autorizou esse calendário. Digite 'configurações' para conectar."
        )
        return {"status": "no_auth"}

    # 4. Ações
    if intent["action"] == "create":
        event_id = google_calendar.create_event(tokens, intent)
        save_event(user["id"], "google", event_id, intent["title"], intent["datetime"])
        twilio_service.send_message(
            user_number,
            f"✅ Evento agendado: {intent['title']} em {intent['datetime']}"
        )

    elif intent["action"] == "delete":
        # Exemplo futuro: google_calendar.delete_event()
        twilio_service.send_message(
            user_number,
            f"🗑️ Solicitação para remover evento: {intent.get('title','[sem título]')}"
        )

    return {"status": "ok"}
