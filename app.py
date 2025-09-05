import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
import uvicorn
import os

from services import twilio_service, openai_service, supabase_client

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")


@app.get("/")
async def root():
    return {"status": "✅ Secretária Pessoal no WhatsApp rodando com sucesso!"}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(None),
    MediaUrl0: str = Form(None),
    NumMedia: int = Form(0),
):
    """
    Webhook principal do Twilio.
    Recebe mensagens de texto ou áudio do WhatsApp, processa com IA e responde.
    """
    try:
        logger.info(f"📩 Mensagem recebida de {From}: {Body or '[Áudio]'}")

        # Sempre avisa que está processando
        await twilio_service.send_message(From, "⏳ Estou analisando sua mensagem...")

        # Se for áudio
        if NumMedia and MediaUrl0:
            transcript = await openai_service.transcribe_audio(MediaUrl0)
            if not transcript:
                await twilio_service.send_message(
                    From, "⚠️ Não consegui entender o áudio. Tente novamente."
                )
                return PlainTextResponse("OK", status_code=200)

            logger.info(f"🎙️ Áudio transcrito: {transcript}")
            reply = await openai_service.process_text_message(transcript)

        # Se for texto
        else:
            reply = await openai_service.process_text_message(Body)

        logger.info(f"🤖 Resposta da IA: {reply}")

        # Envia resposta para o usuário
        await twilio_service.send_message(From, reply)

        return PlainTextResponse("OK", status_code=200)

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        await twilio_service.send_message(
            From, "⚠️ Ocorreu um erro ao processar sua mensagem."
        )
        return PlainTextResponse("ERROR", status_code=500)


# 🚀 Para rodar localmente
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
