import os
import logging
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from services.supabase_client import save_token, get_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Escopos necessários para criar eventos
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service(user_id="default"):
    """
    Recupera o serviço do Google Calendar usando token armazenado no Supabase.
    """
    try:
        token_data = get_token(user_id)
        if not token_data:
            logger.warning("⚠️ Nenhum token encontrado, usuário precisa autorizar o acesso.")
            return None

        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        service = build("calendar", "v3", credentials=creds)
        return service
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar Google Calendar: {e}")
        return None

def create_event(meeting_info: dict, user_id="default"):
    """
    Cria um evento no Google Calendar com base nas informações extraídas pela IA.
    meeting_info esperado:
      {
        "titulo": "Reunião sobre o projeto X",
        "data_hora": "amanhã às 14h",
        "local": "escritório",
        "notas": "Participante: João"
      }
    """
    try:
        service = get_calendar_service(user_id)
        if not service:
            return "⚠️ Não foi possível acessar sua agenda. Autorize o Google Calendar."

        # Interpretação da data/hora (a IA pode retornar texto em vez de ISO)
        start_time, end_time = parse_datetime(meeting_info.get("data_hora"))

        event = {
            "summary": meeting_info.get("titulo", "Reunião"),
            "location": meeting_info.get("local", ""),
            "description": meeting_info.get("notas", ""),
            "start": {"dateTime": start_time, "timeZone": "America/Sao_Paulo"},
            "end": {"dateTime": end_time, "timeZone": "America/Sao_Paulo"},
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()

        logger.info(f"✅ Evento criado: {created_event.get('htmlLink')}")
        return f"📅 Reunião criada: *{meeting_info.get('titulo', 'Reunião')}*\n🕒 {meeting_info.get('data_hora')}\n📍 {meeting_info.get('local', 'Não informado')}\n🔗 {created_event.get('htmlLink')}"

    except Exception as e:
        logger.error(f"❌ Erro ao criar evento no Google Calendar: {e}")
        return "❌ Não foi possível criar a reunião no Google Calendar."

def parse_datetime(data_hora_str: str):
    """
    Converte a string recebida da IA em um intervalo de data/hora.
    - Se a IA retornar texto como 'amanhã às 14h', tenta interpretar.
    - Se for vazio, agenda para 1h após o horário atual.
    """
    try:
        from dateutil import parser, relativedelta

        # Se for vazio, cria para daqui 1h
        if not data_hora_str:
            start = datetime.now() + timedelta(hours=1)
            end = start + timedelta(hours=1)
            return start.isoformat(), end.isoformat()

        # Tenta interpretar texto livre
        start = parser.parse(data_hora_str, fuzzy=True, dayfirst=True)
        end = start + timedelta(hours=1)
        return start.isoformat(), end.isoformat()

    except Exception:
        logger.warning(f"⚠️ Não consegui interpretar '{data_hora_str}', usando 1h a partir de agora.")
        start = datetime.now() + timedelta(hours=1)
        end = start + timedelta(hours=1)
        return start.isoformat(), end.isoformat()
