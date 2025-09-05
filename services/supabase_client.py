import os
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# 🔑 Configuração
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Variáveis SUPABASE_URL e SUPABASE_KEY precisam estar configuradas no .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# -------------------------------
# 🔹 Salvar token no Supabase
# -------------------------------
def save_token(user_phone: str, provider: str, token_data: dict) -> bool:
    """
    Salva ou atualiza o token do usuário no Supabase
    :param user_phone: número do usuário (ex: whatsapp:+556291317326)
    :param provider: provedor do calendário (ex: 'google')
    :param token_data: dicionário com o token e refresh_token
    """
    try:
        logger.info(f"💾 Salvando token para {user_phone} ({provider})")

        resp = supabase.table("calendars").upsert({
            "user_phone": user_phone,
            "provider": provider,
            "token_data": token_data
        }).execute()

        if resp.data:
            logger.info("✅ Token salvo/atualizado com sucesso no Supabase")
            return True
        else:
            logger.warning("⚠️ Nenhum dado retornado ao salvar token")
            return False
    except Exception as e:
        logger.error(f"❌ Erro ao salvar token: {e}")
        return False


# -------------------------------
# 🔹 Buscar token salvo
# -------------------------------
def get_token(user_phone: str, provider: str = "google") -> dict | None:
    """
    Busca o token de um usuário no Supabase
    :param user_phone: número do usuário
    :param provider: provedor (default = google)
    :return: token_data (dict) ou None
    """
    try:
        logger.info(f"🔎 Buscando token de {user_phone} para provider={provider}")

        resp = supabase.table("calendars").select("*").eq("user_phone", user_phone).eq("provider", provider).execute()

        if resp.data and len(resp.data) > 0:
            token = resp.data[0]["token_data"]
            logger.info("✅ Token encontrado")
            return token
        else:
            logger.warning("⚠️ Nenhum token encontrado")
            return None
    except Exception as e:
        logger.error(f"❌ Erro ao buscar token: {e}")
        return None


# -------------------------------
# 🔹 Remover token
# -------------------------------
def delete_token(user_phone: str, provider: str = "google") -> bool:
    """
    Remove o token do usuário (ex: logout)
    """
    try:
        logger.info(f"🗑️ Removendo token de {user_phone} para provider={provider}")

        resp = supabase.table("calendars").delete().eq("user_phone", user_phone).eq("provider", provider).execute()

        if resp.data:
            logger.info("✅ Token removido com sucesso")
            return True
        else:
            logger.warning("⚠️ Nenhum token encontrado para remover")
            return False
    except Exception as e:
        logger.error(f"❌ Erro ao remover token: {e}")
        return False
