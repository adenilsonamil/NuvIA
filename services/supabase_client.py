# services/supabase_client.py

import os
import logging
import httpx

# Variáveis de ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

logger = logging.getLogger(__name__)


async def get_calendar_token(user_phone: str, provider: str = "google"):
    """
    Busca o token de calendário no Supabase.
    :param user_phone: Número do WhatsApp no formato whatsapp:+55xxxxxxxxx
    :param provider: Provedor do calendário (default: google)
    :return: Access token ou None se não encontrado
    """
    try:
        url = f"{SUPABASE_URL}/rest/v1/calendars"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        params = {
            "select": "*",
            "user_phone": f"eq.{user_phone}",
            "provider": f"eq.{provider}"
        }

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers, params=params)

        if resp.status_code == 200:
            data = resp.json()
            if data:
                token = data[0].get("access_token")
                logger.info(f"✅ Token encontrado para {user_phone}")
                return token
            else:
                logger.warning(f"⚠️ Nenhum token encontrado para {user_phone}")
                return None
        else:
            logger.error(f"❌ Erro Supabase ({resp.status_code}): {resp.text}")
            return None

    except Exception as e:
        logger.error(f"❌ Falha ao buscar token Supabase: {e}")
        return None


async def save_calendar_token(user_phone: str, provider: str, access_token: str):
    """
    Salva ou atualiza o token de calendário no Supabase.
    """
    try:
        url = f"{SUPABASE_URL}/rest/v1/calendars"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "user_phone": user_phone,
            "provider": provider,
            "access_token": access_token
        }

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, headers=headers, json=payload)

        if resp.status_code in [200, 201]:
            logger.info(f"✅ Token salvo/atualizado para {user_phone}")
            return True
        else:
            logger.error(f"❌ Erro ao salvar token: {resp.text}")
            return False

    except Exception as e:
        logger.error(f"❌ Falha ao salvar token Supabase: {e}")
        return False
