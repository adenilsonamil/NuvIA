import logging
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from services import twilio_service, openai_service, google_calendar
from datetime import timedelta, datetime

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")


@app.get("/")
async def root():
    return {"status": "🤖 Bot de agenda ativo!"}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    try:
        form = await request.form()
        from_number = form.get("From")
        user_message = form.get("Body", "").strip()

        logger.info(f"📩 Mensagem recebida de {from_number}: {user_message}")

        # Usa IA para interpretar a mensagem e extrair infos de reunião
        meeting_info = await openai_service.extract_meeting_info(user_message)

        if meeting_info:
            summary = meeting_info.get("summary", "Reunião")
            start_time = meeting_info.get("start_time")
            end_time = meeting_info.get("end_time")

            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time)

            event = google_calendar.create_event(summary, start_time, end_time)

            if event:
                response = f"✅ Reunião '{summary}' agendada para {start_time.strftime('%d/%m/%Y %H:%M')}."
            else:
                response = "⚠️ Não consegui criar a reunião, verifique a autenticação do Google Calendar."
        else:
            response = "🤖 Posso ajudar a agendar reuniões e lembretes. Exemplo: 'amanhã às 14h reunião com equipe'."

        await twilio_service.send_message(from_number, response)
        return PlainTextResponse("OK", status_code=200)

    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return PlainTextResponse("Erro interno", status_code=500)
