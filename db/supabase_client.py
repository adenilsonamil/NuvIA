from supabase import create_client
import config
from datetime import datetime, timedelta

# Inicializa o cliente Supabase
supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

# ===============================
# Usuários
# ===============================
def get_or_create_user(phone_number: str, name: str = None):
    """Busca usuário pelo número de telefone, se não existir cria."""
    result = supabase.table("users").select("*").eq("phone_number", phone_number).execute()
    if result.data:
        return result.data[0]
    
    new_user = {
        "phone_number": phone_number,
        "name": name
    }
    response = supabase.table("users").insert(new_user).execute()
    return response.data[0] if response.data else None


# ===============================
# Calendários (tokens OAuth)
# ===============================
def save_calendar_tokens(user_id: str, provider: str, access_token: str,
                         refresh_token: str = None, client_id: str = None,
                         client_secret: str = None, expires_at: int = None):
    """Salva tokens de calendário (Google, Outlook, Apple)."""
    
    expiration_time = None
    if expires_at:
        expiration_time = datetime.utcnow() + timedelta(seconds=expires_at)
    
    record = {
        "user_id": user_id,
        "provider": provider,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "expires_at": expiration_time
    }
    
    # Se já existir, atualiza
    existing = supabase.table("calendars").select("*").eq("user_id", user_id).eq("provider", provider).execute()
    if existing.data:
        return supabase.table("calendars").update(record).eq("id", existing.data[0]["id"]).execute()
    
    # Caso contrário, cria
    return supabase.table("calendars").insert(record).execute()


def get_user_tokens(user_id: str, provider: str):
    """Retorna tokens de um usuário para o provedor especificado."""
    result = supabase.table("calendars").select("*").eq("user_id", user_id).eq("provider", provider).execute()
    return result.data[0] if result.data else None


# ===============================
# Eventos
# ===============================
def save_event(user_id: str, provider: str, event_id: str, title: str, datetime_str: str):
    """Salva evento criado/atualizado pelo bot."""
    record = {
        "user_id": user_id,
        "provider": provider,
        "event_id": event_id,
        "title": title,
        "datetime": datetime_str
    }
    return supabase.table("events").insert(record).execute()


def get_events(user_id: str, provider: str):
    """Lista eventos de um usuário para determinado provedor."""
    result = supabase.table("events").select("*").eq("user_id", user_id).eq("provider", provider).execute()
    return result.data if result.data else []


def delete_event(user_id: str, provider: str, event_id: str):
    """Remove evento salvo localmente (não remove no provedor)."""
    return supabase.table("events").delete().eq("user_id", user_id).eq("provider", provider).eq("event_id", event_id).execute()
