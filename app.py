import os
import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from services import twilio_service, openai_service, google_calendar

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def home():
    return {"status": "✅ Secretaria Virtual rodando com sucesso!"}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...)
):
    """
    Webhook do Twilio para receber mensagens do WhatsApp
    """
    try:
        logger.info(f"📩 Mensagem recebida de {From}: {Body}")

        # Interpretação da mensagem usando OpenAI
        meeting_info = await openai_service.extract_meeting_info(Body)

        if not meeting_info or "data_hora" not in meeting_info:
            resposta = "❌ Não consegui entender os detalhes da reunião. Pode repetir de outra forma?"
            await twilio_service.send_message(From, resposta)
            return PlainTextResponse("OK")

        # Criar evento no Google Calendar
        event = await google_calendar.create_event(
            titulo=meeting_info.get("titulo", "Reunião"),
            data_hora=meeting_info["data_hora"],
            local=meeting_info.get("local", ""),
            notas=meeting_info.get("notas", "")
        )

        # Montar resposta humanizada
        resposta = (
            "📅 Reunião confirmada!\n"
            f"• **Título**: {meeting_info.get('titulo', 'Reunião')}\n"
            f"• **Data/Hora**: {meeting_info['data_hora']}\n"
        )

        if meeting_info.get("local"):
            resposta += f"• **Local**: {meeting_info['local']}\n"
        if meeting_info.get("notas"):
            resposta += f"• **Notas**: {meeting_info['notas']}\n"

        resposta += "✅ Evento adicionado ao Google Calendar."

        # Enviar confirmação para o usuário
        await twilio_service.send_message(From, resposta)
        logger.info("✅ Evento criado e resposta enviada")

        return PlainTextResponse("OK")

    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        await twilio_service.send_message(
            From,
            "⚠️ Ocorreu um erro ao tentar registrar sua reunião. Tente novamente em instantes."
        )
        return PlainTextResponse("Erro interno", status_code=500)
