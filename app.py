import logging
import os
import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from services import twilio_service, openai_service, google_calendar, supabase_client

from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials

# Configuração
app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://nuvia-pk4n.onrender.com/google/callback")
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# =============================
# 🔗 OAuth - Conectar Google
# =============================
@app.get("/google/connect")
async def google_connect(user_phone: str):
    """Inicia o fluxo OAuth do Google Calendar"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI,
    )
    flow.params["access_type"] = "offline"
    flow.params["include_granted_scopes"] = "true"

    auth_url, state = flow.authorization_url(prompt="consent")
    supabase_client.save_state(user_phone, state)  # salva o state temporário no Supabase
    return RedirectResponse(auth_url)

@app.get("/google/callback")
async def google_callback(request: Request):
    """Recebe o retorno do OAuth e salva o token no Supabase"""
    try:
        state = request.query_params.get("state")
        code = request.query_params.get("code")

        user_phone = supabase_client.get_user_by_state(state)
        if not user_phone:
            return PlainTextResponse("⚠️ Usuário não encontrado para esse state.", status_code=400)

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES,
            redirect_uri=GOOGLE_REDIRECT_URI,
        )
        flow.fetch_token(code=code)

        creds = flow.credentials
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }

        supabase_client.save_token(user_phone, "google", token_data)
        return PlainTextResponse("✅ Conta Google conectada com sucesso! Pode voltar ao WhatsApp.")
    except Exception as e:
        logger.error(f"❌ Erro no callback: {e}")
        return PlainTextResponse("Erro ao conectar sua conta Google.", status_code=500)

# =============================
# 📲 Webhook WhatsApp
# =============================
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(""),
    MediaUrl0: str = Form(None)
):
    """Recebe mensagens do WhatsApp (texto ou áudio)."""
    try:
        logger.info(f"📩 Mensagem recebida de {From}: {Body if Body else '[AUDIO]'}")

        # Se veio áudio → transcreve
        if MediaUrl0 and "audio" in MediaUrl0:
            transcription = await openai_service.transcribe_audio(MediaUrl0)
            user_message = transcription
            logger.info(f"📝 Transcrição do áudio: {transcription}")
        else:
            user_message = Body

        # Extrair info da mensagem
        event_info = await openai_service.extract_meeting_info(user_message)

        # Buscar token no Supabase
        token = supabase_client.get_token(From, provider="google")
        if not token:
            response = (
                "📌 Para agendar eventos, preciso que você conecte seu Google Calendar.\n"
                f"Clique aqui para conectar: https://nuvia-pk4n.onrender.com/google/connect?user_phone={From}"
            )
        else:
            # Criar evento no Google Calendar
            event_id = google_calendar.create_event(token, event_info)
            response = (
                f"✅ Reunião agendada!\n\n"
                f"📌 {event_info.get('titulo', 'Reunião')}\n"
                f"📅 {event_info.get('data_hora')}\n"
                f"📍 {event_info.get('local', 'Não informado')}\n"
                f"📝 {event_info.get('notas', '')}"
            )

        await twilio_service.send_message(From, response)
        return PlainTextResponse("OK")

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        await twilio_service.send_message(From, "⚠️ Ocorreu um erro ao processar sua mensagem.")
        return PlainTextResponse("ERROR", status_code=500)

@app.get("/")
async def root():
    return {"status": "✅ NuvIA rodando", "version": "1.0"}
