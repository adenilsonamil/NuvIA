# services/twilio_service.py
import os
import logging
from twilio.rest import Client

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")  # <- precisa vir do .env

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


async def send_message(to: str, body: str):
    """
    Envia mensagem pelo WhatsApp usando Twilio
    """
    try:
        logger.info(f"📤 Enviando mensagem de {TWILIO_WHATSAPP_NUMBER} para {to}: {body}")

        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,  # <-- garante que usa do .env
            to=to,
            body=body
        )

        logger.info(f"✅ Mensagem enviada com SID: {message.sid}")
        return message
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem para {to}: {e}")
        return None
