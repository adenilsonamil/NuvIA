import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from services import twilio_service, openai_service, google_calendar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "🤖 Secretaria pessoal rodando."}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    try:
        data = await request.form()
        user_message = data.get("Body", "").strip()
        from_number = data.get("From")

        logger.info(f"📩 Mensagem recebida de {from_number}: {user_message}")

        # Interpreta a mensagem usando IA
        meeting_info = openai_service.extract_meeting_info(user_message)

        if meeting_info:
            # Cria a reunião direto no Google Calendar
            response = google_calendar.create_event(meeting_info)

            # Responde para o usuário
            twilio_service.send_message(from_number, response)
        else:
            # Se não for reunião, responde de forma genérica
            fallback = "🤖 Posso ajudar a agendar reuniões e lembretes. Diga algo como: 'Agende uma reunião amanhã às 14h no escritório'."
            twilio_service.send_message(from_number, fallback)

        return JSONResponse(content={"status": "success"}, status_code=200)

    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
