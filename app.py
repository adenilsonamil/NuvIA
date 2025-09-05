import os
import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
import openai
import httpx

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Configurações fixas
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "SUA_CHAVE_OPENAI")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

openai.api_key = OPENAI_API_KEY

# Inicialização do FastAPI
app = FastAPI()


# Função para processar texto com GPT
async def process_text_message(message: str) -> str:
    logger.info(f"🤖 Enviando mensagem para OpenAI: {message}")

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é uma secretária pessoal que ajuda com calendários e lembretes."},
                {"role": "user", "content": message}
            ]
        )
        reply = response.choices[0].message["content"]
        logger.info(f"🤖 Resposta da IA: {reply}")
        return reply
    except Exception as e:
        logger.error(f"❌ Erro na OpenAI: {e}")
        return "⚠️ Erro ao processar sua mensagem."


# Função para transcrever áudio com Whisper
async def transcribe_audio(media_url: str) -> str:
    logger.info(f"🎙️ Transcrevendo áudio de {media_url}")

    try:
        async with httpx.AsyncClient() as client:
            audio = await client.get(media_url)
            audio_bytes = audio.content

        transcript = await openai.Audio.atranscribe(
            "whisper-1",
            file=("audio.ogg", audio_bytes, "audio/ogg")
        )
        text = transcript["text"]
        logger.info(f"🎙️ Transcrição: {text}")
        return text
    except Exception as e:
        logger.error(f"❌ Erro ao transcrever áudio: {e}")
        return None


# Rota raiz (teste)
@app.get("/")
async def root():
    return {"message": "🤖 Secretária pessoal online!"}


# Webhook do Twilio (entrada de mensagens WhatsApp)
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
        # Caso seja áudio
        if NumMedia != "0" and MediaUrl0:
            await msg.body("🔎 Analisando seu áudio, aguarde...")
            text = await transcribe_audio(MediaUrl0)
            if not text:
                msg.body("⚠️ Não consegui transcrever seu áudio. Tente novamente.")
            else:
                reply = await process_text_message(text)
                msg.body(f"✅ Transcrição: {text}\n\n🤖 {reply}")

        # Caso seja texto
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
                await msg.body("🔎 Analisando suas informações, aguarde...")
                reply = await process_text_message(Body)
                msg.body(f"🤖 {reply}")

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        msg.body("⚠️ Ocorreu um erro ao processar sua mensagem.")

    return PlainTextResponse(str(resp), media_type="application/xml")
