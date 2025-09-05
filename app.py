import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from services import twilio_service, openai_service

app = FastAPI()
logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO)

@app.get("/")
async def root():
    return {"status": "✅ API funcionando"}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(None),
    MediaUrl0: str = Form(None)
):
    """
    Webhook que recebe mensagens do WhatsApp via Twilio.
    """
    try:
        logger.info(f"📩 Mensagem recebida de {From}: {Body or '[áudio]'}")

        reply = None

        if Body:
            # Mensagem de texto → envia para GPT
            logger.info(f"🤖 Enviando para GPT: {Body}")
            reply = await openai_service.get_chat_response(Body)

        elif MediaUrl0:
            # Mensagem de áudio → transcreve e envia para GPT
            logger.info(f"🎤 Áudio recebido de {From}: {MediaUrl0}")
            transcript = await openai_service.transcribe_audio(MediaUrl0)
            logger.info(f"📝 Transcrição: {transcript}")
            reply = await openai_service.get_chat_response(transcript)

        if reply:
            logger.info(f"🤖 Resposta da IA: {reply}")
            twilio_service.send_message(From, reply)  # 🔹 sem await
        else:
            logger.warning("⚠️ Nenhuma resposta gerada pela IA")
            twilio_service.send_message(From, "⚠️ Não consegui entender sua mensagem.")

        return PlainTextResponse("OK", status_code=200)

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        # 🔹 envia mensagem de erro sem await
        twilio_service.send_message(From, "⚠️ Ocorreu um erro ao processar sua mensagem.")
        return PlainTextResponse("Erro interno", status_code=500)
