from twilio.rest import Client
import config

client = Client(config.TWILIO_SID, config.TWILIO_AUTH_TOKEN)

def send_message(to, body):
    client.messages.create(
        from_=f"whatsapp:{config.TWILIO_PHONE}",
        to=to,
        body=body
    )
