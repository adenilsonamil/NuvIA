import os
import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from services import openai_service, supabase_client, twilio_service

# Configurações
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = FastAPI(title="Nuvia Assistant")

# Página inicial
@app.get("/")
async def root():
    return {"status": "✅ API está rodando"}


# Webhook do WhatsApp
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form("")
):
    try:
        logger.info(f"📩 Mensagem recebida de {From}: {Body}")

        # 🔎 Extrair informações com OpenAI
        logger.info(f"services.openai_service:🔎 Extraindo informações da mensagem: {Body}")
        response = await openai_service.process_message(Body)

        # 🔎 Buscar token no Supabase
        token = await supabase_client.get_token(From, provider="google")

        if not token:
            msg = (
                "📌 Para agendar eventos, preciso que você conecte seu Google Calendar.\n"
                f"Clique aqui para conectar: {os.getenv('BASE_URL', 'https://nuvia-pk4n.onrender.com')}/google/connect?user_phone={From}"
            )
            await twilio_service.send_message(From, msg)
            return JSONResponse(content={"status": "ok", "message": "Token ausente, instrução enviada"})

        # Se tiver token, responde normalmente
        if response:
            await twilio_service.send_message(From, response)
        else:
            await twilio_service.send_message(From, "⚠️ Não consegui entender sua mensagem.")

        return JSONResponse(content={"status": "ok"})

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        # Envia fallback de erro
        try:
            await twilio_service.send_message(From, "⚠️ Ocorreu um erro ao processar sua mensagem.")
        except Exception as e2:
            logger.error(f"❌ Falha ao enviar fallback: {e2}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# Endpoint para conectar Google (simulação simples)
@app.get("/google/connect")
async def google_connect(user_phone: str):
    logger.info(f"🔗 Usuário {user_phone} acessou a página de conexão do Google.")
    return {
        "status": "ok",
        "message": f"Usuário {user_phone} deve autenticar com o Google aqui."
    }
