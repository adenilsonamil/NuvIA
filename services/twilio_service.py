import os
from twilio.rest import Client

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_message(to: str, message: str):
    """
    Envia mensagem de WhatsApp pelo Twilio.
    """
    try:
        msg = client.messages.create(
            from_=f"whatsapp:{TWILIO_PHONE}",
            body=message,
            to=to
        )
        print(f"✅ Mensagem enviada com SID: {msg.sid}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem pelo Twilio: {e}")
