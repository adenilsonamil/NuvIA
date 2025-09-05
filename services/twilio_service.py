import os
import logging
from twilio.rest import Client

# Configuração de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Credenciais do Twilio (carregadas de variáveis de ambiente)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")  # Ex: "whatsapp:+14155238886"

# Cliente Twilio
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Função assíncrona para envio de mensagem
async def send_message(to: str, body: str):
    """
    Envia uma mensagem pelo WhatsApp usando Twilio.
    """
    try:
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
