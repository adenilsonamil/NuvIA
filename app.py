import os
import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from twilio.twiml.messaging_response import MessagingResponse
from google_auth_oauthlib.flow import Flow

from services.twilio_service import send_message
from services.openai_service import extract_meeting_info
from services.google_calendar import create_event
from services.supabase_client import save_token, get_token

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Variáveis de ambiente
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://nuvia-pk4n.onrender.com/auth/google/callback")

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Inicializa app
app = FastAPI()


@app.get("/")
async def root():
    return {"status": "🤖 Secretaria Pessoal rodando com sucesso!"}


# 🔹 Fluxo OAuth do Google
@app.get("/auth/google")
def auth_google():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    return RedirectResponse(auth_url)


@app.get("/auth/google/callback")
def auth_google_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "❌ Nenhum código de autorização recebido."}

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(code=code)

    credentials = flow.credentials
    token = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": list(credentials.scopes),
    }

    # Salva no Supabase
    save_token("google", token)

    return {"status": "✅ Token do Google salvo no Supabase com sucesso!"}


# 🔹 Webhook do WhatsApp
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...)
):
    user_number = From
    user_message = Body.strip()

    logger.info(f"📩 Mensagem recebida de {user_number}: {user_message}")

    try:
        # Extrair informações com IA
        meeting_info = await extract_meeting_info(user_message)
        logger.info(f"✅ Extraído: {meeting_info}")

        # Recuperar token do Google
        google_token = get_token("google")
        if not google_token:
            response_text = (
                "⚠️ Você ainda não vinculou seu Google Calendar.\n\n"
                "👉 Acesse este link para autorizar: "
                f"{os.getenv('BASE_URL', 'https://nuvia-pk4n.onrender.com')}/auth/google"
            )
            await send_message(user_number, response_text)
            return {"status": "⚠️ Google não autorizado"}

        # Criar evento no Google Calendar
        event = create_event(google_token, meeting_info)

        response_text = (
            f"📅 Reunião criada com sucesso!\n\n"
            f"**Título:** {meeting_info.get('titulo', 'Reunião')}\n"
            f"**Data/Hora:** {meeting_info.get('data_hora', 'Não identificado')}\n"
            f"**Local:** {meeting_info.get('local', 'Não informado')}\n"
            f"**Notas:** {meeting_info.get('notas', 'Nenhuma')}\n"
            f"✅ Link do evento: {event.get('htmlLink', 'Não disponível')}"
        )

        await send_message(user_number, response_text)
        return {"status": "✅ Evento criado e usuário notificado."}

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        twilio_resp = MessagingResponse()
        twilio_resp.message("❌ Ocorreu um erro ao processar sua solicitação.")
        return str(twilio_resp)
