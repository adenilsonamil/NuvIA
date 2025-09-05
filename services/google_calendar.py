import logging
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from services.supabase_client import save_token, get_token

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    """Inicializa o serviço Google Calendar com o token salvo no Supabase"""
    try:
        token_data = get_token("google")  # agora passando o provider corretamente
        if not token_data:
            logger.error("❌ Nenhum token do Google encontrado no Supabase")
            return None

        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        service = build("calendar", "v3", credentials=creds)
        return service

    except Exception as e:
        logger.error(f"❌ Erro ao inicializar Google Calendar: {e}")
        return None


def create_event(summary: str, start_time: datetime.datetime, end_time: datetime.datetime):
    """Cria um evento no Google Calendar"""
    try:
        service = get_calendar_service()
        if not service:
            return None

        event = {
            "summary": summary,
            "start": {"dateTime": start_time.isoformat(), "timeZone": "America/Sao_Paulo"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "America/Sao_Paulo"},
        }

        event_result = service.events().insert(calendarId="primary", body=event).execute()
        logger.info(f"✅ Evento criado: {event_result.get('htmlLink')}")
        return event_result

    except Exception as e:
        logger.error(f"❌ Erro ao criar evento no Calendar: {e}")
        return None


def save_google_token(token: dict):
    """Salva o token de autenticação do Google no Supabase"""
    try:
        save_token("google", token)  # provider fixado
        logger.info("✅ Token do Google salvo no Supabase")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar token do Google: {e}")
