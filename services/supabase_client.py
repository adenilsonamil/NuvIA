import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========= FUNÇÕES PARA MENSAGENS ==========
def save_message(user_number: str, text: str, sender: str):
    """Salva mensagens trocadas no banco"""
    supabase.table("messages").insert({
        "user_number": user_number,
        "text": text,
        "sender": sender
    }).execute()

def get_messages(user_number: str):
    """Busca mensagens do usuário"""
    response = supabase.table("messages").select("*").eq("user_number", user_number).execute()
    return response.data if response.data else []

# ========= FUNÇÕES PARA TOKENS ==========
def save_token(user_id: str, provider: str, tokens: dict):
    """
    Salva ou atualiza tokens de integração (Google, etc.)
    Estrutura da tabela 'tokens':
        - user_id (string)
        - provider (string: google, etc.)
        - access_token
        - refresh_token
        - expires_in
    """
    # Deleta se já existir (para atualizar)
    supabase.table("tokens").delete().eq("user_id", user_id).eq("provider", provider).execute()

    supabase.table("tokens").insert({
        "user_id": user_id,
        "provider": provider,
        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
        "expires_in": tokens.get("expires_in"),
    }).execute()

def get_token(user_id: str, provider: str):
    """Recupera o token de um usuário para o provider (ex: google)"""
    response = supabase.table("tokens").select("*").eq("user_id", user_id).eq("provider", provider).execute()
    if response.data:
        return response.data[0]
    return None
