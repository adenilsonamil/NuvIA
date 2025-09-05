import os
import logging
from twilio.rest import Client

# Configuração do logger
logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_PHONE = os.getenv("TWILIO_PHONE", "").strip()

# Inicializa o cliente do Twilio
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)


def send_whatsapp_message(to: str, body: str):
    """
    Envia mensagem de WhatsApp via Twilio.
    """
    try:
        if not TWILIO_PHONE:
            logger.error("❌ TWILIO_PHONE não configurado no .env")
            return None

        logger.info(f"📤 Enviando mensagem para {to}: {body}")

        message = client.messages.create(
            from_=TWILIO_PHONE,
            to=to,
            body=body
        )

        logger.info(f"✅ Mensagem enviada com SID: {message.sid}")
        return message.sid

    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem para {to}: {e}")
        return None


# Alias para retrocompatibilidade
send_message = send_whatsapp_message
