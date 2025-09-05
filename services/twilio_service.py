import logging
import os
from twilio.rest import Client

logger = logging.getLogger("services.twilio_service")

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(TWILIO_SID, TWILIO_TOKEN)

async def send_message(to_number: str, body: str):
    """Envia mensagem WhatsApp pelo Twilio."""
    try:
        msg = client.messages.create(
            from_=f"whatsapp:{TWILIO_PHONE}",
            to=to_number,
            body=body
        )
        logger.info(f"✅ Mensagem enviada com SID: {msg.sid}")
        return msg.sid
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem para {to_number}: {e}")
        return None
