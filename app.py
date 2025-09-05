import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from services import twilio_service, openai_service, google_calendar, supabase_client

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(""),
    MediaUrl0: str = Form(None)
):
    """
    Webhook que recebe mensagens do WhatsApp via Twilio.
    Suporta texto e áudio.
    """
    try:
        logger.info(f"📩 Mensagem recebida de {From}: {Body if Body else '[AUDIO]'}")

        # Se veio áudio → transcreve
        if MediaUrl0 and "audio" in MediaUrl0:
            transcription = await openai_service.transcribe_audio(MediaUrl0)
            user_message = transcription
            logger.info(f"📝 Transcrição do áudio: {transcription}")
        else:
            user_message = Body

        # Extrair info da mensagem
        event_info = await openai_service.extract_meeting_info(user_message)

        # Buscar token no Supabase
        token = supabase_client.get_token(From, provider="google")
        if not token:
            response = (
                "📌 Para agendar eventos, preciso que você conecte seu Google Calendar.\n"
                "Clique aqui para conectar: https://nuvia-pk4n.onrender.com/google/connect"
            )
        else:
            # Criar evento no Google Calendar
            event_id = google_calendar.create_event(token, event_info)
            response = (
                f"✅ Reunião agendada!\n\n"
                f"📌 {event_info.get('titulo', 'Reunião')}\n"
                f"📅 {event_info.get('data_hora')}\n"
                f"📍 {event_info.get('local', 'Não informado')}\n"
                f"📝 {event_info.get('notas', '')}"
            )

        # Enviar resposta pelo WhatsApp
        await twilio_service.send_message(From, response)
        return PlainTextResponse("OK")

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        await twilio_service.send_message(From, "⚠️ Ocorreu um erro ao processar sua mensagem.")
        return PlainTextResponse("ERROR", status_code=500)
