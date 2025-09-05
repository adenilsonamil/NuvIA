import logging
from supabase import create_client
import os
import json

logger = logging.getLogger("services.supabase_client")

# Configura Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_token(provider: str, token: dict):
    """
    Salva o token no Supabase, vinculado ao provider (ex: 'google')
    """
    try:
        data = {
            "provider": provider,
            "token": json.dumps(token)
        }
        supabase.table("tokens").upsert(data).execute()
        logger.info(f"✅ Token salvo no Supabase para provider={provider}")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar token: {e}")


def get_token(provider: str):
    """
    Recupera o token do Supabase para o provider informado (ex: 'google')
    """
    try:
        result = supabase.table("tokens").select("*").eq("provider", provider).execute()
        if result.data and len(result.data) > 0:
            token_data = result.data[0]["token"]
            return json.loads(token_data)
        else:
            logger.warning(f"⚠️ Nenhum token encontrado para provider={provider}")
            return None
    except Exception as e:
        logger.error(f"❌ Erro ao buscar token: {e}")
        return None
