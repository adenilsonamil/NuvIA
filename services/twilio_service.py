import os
import logging
from twilio.rest import Client

# Configuração de logs
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE", "").strip()

# 🔧 Corrige o número para sempre ter o prefixo whatsapp:
if TWILIO_PHONE and not TWILIO_PHONE.startswith("whatsapp:"):
    TWILIO_PHONE = f"whatsapp:{TWILIO_PHONE}"

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    logger.error("❌ TWILIO_ACCOUNT_SID ou TWILIO_AUTH_TOKEN não configurados!")

if not TWILIO_PHONE:
    logger.error("❌ TWILIO_PHONE não configurado corretamente!")

# Cliente Twilio
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_whatsapp_message(to: str, message: str):
    """
    Envia uma mensagem de WhatsApp usando Twilio.
    
    Args:
        to (str): Número de destino (ex: 'whatsapp:+556291317326').
        message (str): Texto da mensagem.

    Returns:
        str: SID da mensagem enviada.
    """
    try:
        # 🔧 Corrige destino se não tiver prefixo whatsapp:
        if not to.startswith("whatsapp:"):
            to = f"whatsapp:{to}"

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
