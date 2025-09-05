import os
import logging
from twilio.rest import Client

# Carrega credenciais do ambiente
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")  # Ex: "whatsapp:+14155238886"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_message(to: str, body: str):
    """
    Envia mensagem WhatsApp via Twilio
    :param to: Número de destino (formato whatsapp:+55...)
    :param body: Texto da mensagem
    :return: SID da mensagem enviada
    """
    try:
        if not TWILIO_WHATSAPP_NUMBER:
            raise ValueError("Número remetente TWILIO_WHATSAPP_NUMBER não configurado.")

        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to,
            body=body
        )

        logging.info(f"📤 Mensagem enviada para {to} com SID: {message.sid}")
        return message.sid

    except Exception as e:
        logging.error(f"❌ Erro ao enviar mensagem para {to}: {e}")
        return None
