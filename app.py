import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from services import openai_service, supabase_client, twilio_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "🤖 Secretária pessoal online!"}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(""),
    NumMedia: str = Form("0"),
    MediaUrl0: str = Form(None)
):
    logger.info(f"📩 Mensagem recebida de {From}: {Body if Body else '[áudio]'}")
    resp = MessagingResponse()
    msg = resp.message()

    try:
        # Áudio
        if NumMedia != "0" and MediaUrl0:
            msg.body("🔎 Transcrevendo seu áudio...")
            text = await openai_service.transcribe_audio(MediaUrl0)
            if text:
                reply = await openai_service.process_text_message(text)
                msg.body(f"✅ Transcrição: {text}\n\n🤖 {reply}")
            else:
                msg.body("⚠️ Não consegui transcrever seu áudio.")

        # Texto
        else:
            if Body.strip().lower() in ["oi", "olá", "ola", "configurações", "configuracoes"]:
                menu = (
                    "👋 Olá, eu sou sua secretária pessoal.\n"
                    "Quais calendários deseja vincular?\n\n"
                    "1️⃣ Google Calendar\n"
                    "2️⃣ Outlook Calendar\n"
                    "3️⃣ Apple Calendar\n"
                    "4️⃣ Configurações\n\n"
                    "Digite o número da opção desejada."
                )
                msg.body(menu)
            else:
                msg.body("🔎 Analisando suas informações...")
                reply = await openai_service.process_text_message(Body)
                msg.body(f"🤖 {reply}")

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        msg.body("⚠️ Ocorreu um erro ao processar sua mensagem.")

    return PlainTextResponse(str(resp), media_type="application/xml")
