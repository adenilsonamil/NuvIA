import logging
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger("services.supabase_client")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_calendar_token(user_phone: str, provider: str, token: dict):
    """
    Salva ou atualiza token de um calendário
    """
    try:
        data = {
            "user_phone": user_phone,
            "provider": provider,
            "token": token
        }

        existing = supabase.table("calendars").select("*").eq("user_phone", user_phone).eq("provider", provider).execute()

        if existing.data:
            supabase.table("calendars").update(data).eq("user_phone", user_phone).eq("provider", provider).execute()
            logger.info(f"🔄 Token atualizado para {provider} de {user_phone}")
        else:
            supabase.table("calendars").insert(data).execute()
            logger.info(f"✅ Token salvo para {provider} de {user_phone}")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar token: {e}")


def get_calendar_token(user_phone: str, provider: str):
    """
    Busca token do calendário
    """
    try:
        result = supabase.table("calendars").select("*").eq("user_phone", user_phone).eq("provider", provider).execute()
        if result.data:
            return result.data[0]["token"]
        return None
    except Exception as e:
        logger.error(f"❌ Erro ao buscar token: {e}")
        return None
