import logging
import os
from supabase import create_client

logger = logging.getLogger("services.supabase_client")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def get_token(user_phone: str, provider: str = "google") -> dict:
    """Busca token do usuário no Supabase."""
    try:
        response = supabase.table("calendars").select("*").eq("user_phone", user_phone).eq("provider", provider).execute()
        if response.data:
            return response.data[0]
        logger.warning(f"⚠️ Nenhum token encontrado para provider={provider}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro ao buscar token: {e}")
        return None
