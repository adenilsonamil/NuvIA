from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def create_event(tokens, intent):
    creds = Credentials(
        tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=tokens["client_id"],
        client_secret=tokens["client_secret"]
    )

    service = build("calendar", "v3", credentials=creds)
    event = {
        "summary": intent["title"],
        "start": {"dateTime": intent["datetime"], "timeZone": "America/Sao_Paulo"},
        "end": {"dateTime": intent["datetime"], "timeZone": "America/Sao_Paulo"},
    }
    event = service.events().insert(calendarId="primary", body=event).execute()
    return event["id"]
