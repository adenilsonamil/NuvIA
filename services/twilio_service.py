import logging
from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER

logger = logging.getLogger("services.twilio_service")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_message(to: str, body: str):
    try:
        msg = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to,
            body=body
        )
        logger.info(f"✅ Mensagem enviada para {to}, SID: {msg.sid}")
        return msg.sid
    except Exception as e:
        logger.error(f"❌ Erro Twilio: {e}")
        return None
