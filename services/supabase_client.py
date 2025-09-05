from supabase import create_client
import config

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

def save_event(user_number, event_id, intent):
    supabase.table("events").insert({
        "user_id": user_number,
        "provider": intent["calendar"],
        "event_id": event_id,
        "title": intent["title"],
        "datetime": intent["datetime"]
    }).execute()

def get_user_tokens(user_number, provider):
    result = supabase.table("calendars").select("*").eq("user_id", user_number).eq("provider", provider).execute()
    return result.data[0] if result.data else None
