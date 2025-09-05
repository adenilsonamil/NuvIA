import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

from services import openai_service, twilio_service, google_calendar
from db.supabase_client import save_event

load_dotenv()

app = FastAPI()

@app.get("/")
def home():
    return {"status": "✅ Secretária pessoal ativa!"}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    try:
        form = await request.form()
        sender = form.get("From")
        message_body = form.get("Body")

        print(f"📩 Mensagem recebida de {sender}: {message_body}")

        # Interpreta a intenção
        intent_data = openai_service.interpret_text(message_body)
        intent = intent_data.get("intent", "outro")

        reply = ""
        if intent == "reuniao":
            description = intent_data.get("descricao", "Reunião")
            date = intent_data.get("data", None)
            time = intent_data.get("hora", None)

            if date and time:
                google_calendar.create_event(description, date, time)
                reply = f"📅 Reunião agendada: {description} em {date} às {time}."
            else:
                reply = "⚠️ Preciso da data e hora para agendar a reunião."

        elif intent == "lembrete":
            descricao = intent_data.get("descricao", "Lembrete")
            date = intent_data.get("data", None)
            save_event(sender, descricao, date)
            reply = f"⏰ Lembrete criado: {descricao} ({date})."

        elif intent == "outro":
            reply = "🤖 Posso ajudar com reuniões e lembretes. O que deseja registrar?"

        elif intent == "erro":
            reply = intent_data.get("text", "⚠️ Ocorreu um erro na interpretação.")

        else:
            reply = "⚠️ Não entendi sua solicitação. Pode reformular?"

        # Envia resposta pelo Twilio
        print(f"📤 Respondendo para {sender}: {reply}")
        twilio_service.send_whatsapp_message(sender, reply)

        return PlainTextResponse("OK")

    except Exception as e:
        error_msg = f"❌ Erro no processamento: {str(e)}"
        print(error_msg)
        if "From" in locals():
            twilio_service.send_whatsapp_message(sender, error_msg)
        return PlainTextResponse("ERROR", status_code=500)
