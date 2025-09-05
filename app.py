import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from services import twilio_service, openai_service

# Configura logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Cria app FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "🚀 Nuvia está rodando!"}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...),
    NumMedia: int = Form(0),
):
    """
    Webhook que recebe mensagens do WhatsApp via Twilio.
    - Se texto → manda para IA processar texto
    - Se áudio → (futuro) manda transcrever e processar
    """
    try:
        logger.info(f"📩 Mensagem recebida de {From}: {Body}")

        # Caso seja áudio
        if NumMedia and int(NumMedia) > 0:
            logger.info("🎤 Mensagem de áudio recebida - transcrição não implementada ainda")
            reply = await openai_service.process_audio_message("Áudio recebido (simulado)")
        else:
            # Caso seja texto
            reply = await openai_service.process_text_message(Body)

        logger.info(f"🤖 Resposta da IA: {reply}")

        # Envia resposta ao usuário pelo WhatsApp
        await twilio_service.send_whatsapp_message(to_number=From, message=reply)

        return PlainTextResponse("OK", status_code=200)

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        await twilio_service.send_whatsapp_message(
            to_number=From,
            message="⚠️ Ocorreu um erro ao processar sua mensagem."
        )
        return PlainTextResponse("ERROR", status_code=500)
