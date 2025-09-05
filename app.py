from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from services import twilio_service, openai_service, google_calendar
from services.supabase_client import save_message
import logging

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Assistente de Agenda rodando!"}

# === GOOGLE OAUTH ===
@app.get("/google/login")
async def google_login(user_id: str):
    url = google_calendar.get_google_auth_url(user_id)
    return RedirectResponse(url)

@app.get("/google/callback")
async def google_callback(code: str, state: str):
    tokens = google_calendar.exchange_code_for_tokens(code, state)
    return JSONResponse({"message": "Autorização concluída com sucesso!", "tokens": tokens})

# === WEBHOOK TWILIO ===
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.form()
    user_number = data.get("From")
    text = data.get("Body", "").strip().lower()

    logging.info(f"📩 Mensagem recebida de {user_number}: {text}")

    try:
        # Exemplo: se o usuário pede reunião
        if "reunião" in text or "lembrete" in text:
            # aqui o ideal é usar OpenAI para extrair data/hora corretamente
            start_time = "2025-09-06T10:00:00"  
            end_time = "2025-09-06T11:00:00"  

            try:
                event = google_calendar.create_event(user_number, "Reunião Importante", start_time, end_time)
                response_text = f"✅ Reunião criada no seu Google Calendar: {event.get('htmlLink')}"
            except Exception as e:
                response_text = f"⚠️ Preciso que você autorize o Google Calendar. Acesse: https://nuvia-pk4n.onrender.com/google/login?user_id={user_number}"

        else:
            response_text = "🤖 Posso ajudar com reuniões e lembretes. O que deseja registrar?"

        await twilio_service.send_message(user_number, response_text)
        return JSONResponse({"status": "ok"})

    except Exception as e:
        logging.error(f"Erro no webhook: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
