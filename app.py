import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from services import twilio_service, openai_service

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("app")

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Nuvia Assistant online 🚀"}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    try:
        form = await request.form()
        from_number = form.get("From")
        user_message = form.get("Body")

        logger.info(f"📩 Mensagem recebida de {from_number}: {user_message}")

        # Envia a mensagem para GPT
        logger.info(f"🤖 Enviando para GPT: {user_message}")
        reply = await openai_service.get_chat_response(user_message)
        logger.info(f"🤖 Resposta da IA: {reply}")

        # Envia resposta pelo WhatsApp
        await twilio_service.send_message(from_number, reply)

        return PlainTextResponse("OK", status_code=200)

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        try:
            if "from_number" in locals():
                await twilio_service.send_message(from_number, "⚠️ Ocorreu um erro ao processar sua mensagem.")
        except Exception as send_error:
            logger.error(f"❌ Falha ao enviar mensagem de erro pelo Twilio: {send_error}")

        return PlainTextResponse("Erro interno", status_code=500)
