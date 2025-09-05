import logging
import os
from supabase import create_client

logger = logging.getLogger("services.supabase_client")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def save_state(user_phone: str, state: str):
    """Salva o state do OAuth temporário"""
    try:
        supabase.table("oauth_state").insert({"user_phone": user_phone, "state": state}).execute()
    except Exception as e:
        logger.error(f"❌ Erro ao salvar state: {e}")

def get_user_by_state(state: str):
    """Recupera o usuário associado ao state"""
    try:
        resp = supabase.table("oauth_state").select("*").eq("state", state).execute()
        if resp.data:
            return resp.data[0]["user_phone"]
        return None
    except Exception as e:
        logger.error(f"❌ Erro ao buscar state: {e}")
        return None

def save_token(user_phone: str, provider: str, token_data: dict):
    """Salva ou atualiza token de acesso"""
    try:
        supabase.table("calendars").upsert({
            "user_phone": user_phone,
            "provider": provider,
            "token_data": token_data
        }).execute()
        logger.info(f"✅ Token salvo para {user_phone}")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar token: {e}")

