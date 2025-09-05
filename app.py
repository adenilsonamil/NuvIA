from fastapi import FastAPI, Request
from services import twilio_service, openai_service, google_calendar
from db.supabase_client import save_event, get_user_tokens

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Secretária Pessoal Online"}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.form()
    user_number = data.get("From")
    message_type = "audio" if "MediaUrl0" in data else "text"
    content = data.get("Body") if message_type == "text" else data.get("MediaUrl0")

    twilio_service.send_message(user_number, "🔎 Estou analisando suas informações...")

    # 1. Transcreve áudio se necessário
    if message_type == "audio":
        text = openai_service.transcribe_audio(content)
    else:
        text = content

    # 2. Interpreta intenção
    intent = openai_service.interpret_text(text)

    # 3. Verifica tokens
    tokens = get_user_tokens(user_number, intent.get("calendar"))
    if not tokens:
        twilio_service.send_message(user_number, "⚠️ Você ainda não autorizou esse calendário.")
        return {"status": "no_auth"}

    # 4. Criação de evento (Google como exemplo inicial)
    if intent["action"] == "create":
        event_id = google_calendar.create_event(tokens, intent)
        save_event(user_number, event_id, intent)

    twilio_service.send_message(user_number, f"✅ Evento agendado: {intent['title']} em {intent['datetime']}")
    return {"status": "ok"}
