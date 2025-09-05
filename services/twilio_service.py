import os
import logging
from twilio.rest import Client

logger = logging.getLogger("services.twilio_service")

# 🔹 Configuração fixa (sem depender do .env se não quiser)
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = "whatsapp:+14155238886"  # número fixo do Twilio

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_message(to: str, body: str):
    """
    Envia mensagem pelo WhatsApp via Twilio.
    """
    try:
        logger.info(f"📤 Enviando mensagem de {FROM_NUMBER} para {to}: {body}")
        message = client.messages.create(
            from_=FROM_NUMBER,
            to=to,
            body=body
        )
        logger.info(f"✅ Mensagem enviada com SID: {message.sid}")
        return message.sid
    except Exception as e:
        logger.error(f"❌ Erro Twilio: {e}")
        return None
