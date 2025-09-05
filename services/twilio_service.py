import os
import logging
from twilio.rest import Client

logger = logging.getLogger(__name__)

# Forçar leitura correta do número de envio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE", "").strip()

# Correção: garantir prefixo whatsapp:
if TWILIO_PHONE and not TWILIO_PHONE.startswith("whatsapp:"):
    TWILIO_PHONE = f"whatsapp:{TWILIO_PHONE}"

if not TWILIO_PHONE:
    logger.error("❌ TWILIO_PHONE não configurado corretamente. Verifique o .env!")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_message(to: str, message: str):
    """
    Envia mensagem via WhatsApp pelo Twilio
    """
    try:
        logger.info(f"📤 Enviando mensagem para {to} via {TWILIO_PHONE}")
        msg = client.messages.create(
            from_=TWILIO_PHONE,
            body=message,
            to=to
        )
        logger.info(f"✅ Mensagem enviada com SID: {msg.sid}")
        return msg.sid
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem para {to}: {e}")
        raise
