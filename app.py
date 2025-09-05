import os
import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from services import twilio_service, openai_service
from supabase import create_client

# 🔹 Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# 🔹 FastAPI app
app = FastAPI()

# 🔹 Supabase (para tokens de calendário)
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# 🔹 Webhook do WhatsApp
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(None),
    MediaUrl0: str = Form(None),   # URL do áudio enviado
    MediaContentType0: str = Form(None)
):
    logger.info(f"📩 Mensagem recebida de {From}: {Body or '[áudio]'}")

    try:
        # 🔹 Caso seja áudio
        if MediaUrl0 and "audio" in (MediaContentType0 or ""):
            logger.info(f"🎙️ Áudio recebido: {MediaUrl0}")

            # Baixar o áudio para arquivo temporário
            import httpx, tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
            async with httpx.AsyncClient() as client:
                response = await client.get(MediaUrl0, auth=(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")))
                temp_file.write(response.content)
                temp_file.close()

            # Transcreve o áudio
            text_message = await openai_service.process_audio_message(temp_file.name)

            # Passa o texto para interpretação
            reply = await openai_service.process_text_message(text_message)

        else:
            # 🔹 Caso seja texto
            reply = await openai_service.process_text_message(Body)

        # 🔹 Envia a resposta no WhatsApp
        await twilio_service.send_message(From, reply)
        return PlainTextResponse("OK", status_code=200)

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        await twilio_service.send_message(From, "⚠️ Ocorreu um erro ao processar sua mensagem.")
        return PlainTextResponse("Erro", status_code=500)


# 🔹 Rota de teste
@app.get("/")
async def root():
    return {"status": "ok", "message": "Assistente pessoal rodando 🚀"}
