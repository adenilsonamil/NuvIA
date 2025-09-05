import os
from twilio.rest import Client

# Pega credenciais do Twilio das variáveis de ambiente
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")  # Número padrão do Sandbox

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_message(to: str, message: str):
    """
    Envia mensagem de WhatsApp via Twilio.
    :param to: Número destino (exemplo: whatsapp:+556291234567)
    :param message: Texto a ser enviado
    """
    try:
        print(f"📤 Enviando mensagem para {to}: {message}")

        msg = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message,
            to=to
        )
        print(f"✅ Mensagem enviada com SID: {msg.sid}")
        return msg.sid
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem pelo Twilio: {e}")
        return None
