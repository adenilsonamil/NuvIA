import os
import logging
import httpx

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")


async def send_message(to: str, body: str):
    """
    Envia mensagem WhatsApp usando Twilio (versão assíncrona com httpx).
    """
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"

        data = {
            "From": f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            "To": to,
            "Body": body
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, data=data, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))

        if resp.status_code == 201:
            sid = resp.json().get("sid")
            logger.info(f"✅ Mensagem enviada com SID: {sid}")
            return sid
        else:
            logger.error(f"❌ Erro ao enviar mensagem para {to}: {resp.text}")
            return None

    except Exception as e:
        logger.error(f"❌ Falha ao enviar mensagem para {to}: {e}")
        return None
