import logging
from datetime import datetime, timedelta

logger = logging.getLogger("services.google_calendar")

def create_event(token: dict, event_info: dict) -> str:
    """
    Cria evento no Google Calendar.
    (Aqui usamos token salvo no Supabase)
    """
    if not token:
        logger.error("❌ Nenhum token disponível")
        return None

    # Exemplo: simulação (você pode integrar com google-api-python-client)
    logger.info(f"📅 Criando evento: {event_info}")
    return "event_mock_id"
