import os
import logging
from twilio.rest import Client

# Configura o logger
logging.basicConfig(level=logging.INFO)

# Carrega variáveis de ambiente
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")  # Exemplo: whatsapp:+14155238886

# Inicializa o cliente do Twilio
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_message(to: str, body: str):
    """
    Envia mensagem de WhatsApp usando Twilio.
    """
    try:
        if not TWILIO_PHONE:
            raise ValueError("⚠️ TWILIO_PHONE não configurado nas variáveis de ambiente.")

        message = client.messages.create(
            from_=TWILIO_PHONE,
            to=to,
            body=body
        )
        logging.info(f"✅ Mensagem enviada com SID: {message.sid}")
        return message.sid
    except Exception as e:
        logging.error(f"❌ Erro ao enviar mensagem para {to}: {e}")
        return None
