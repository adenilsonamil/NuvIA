import logging
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

from services import twilio_service, openai_service, supabase_client

# Carrega variáveis do .env
load_dotenv()

# Configuração do log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h2>🚀 API de Integração WhatsApp + Google Calendar</h2>"


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    try:
        form = await request.form()
        From = form.get("From")
        Body = form.get("Body")

        logger.info(f"📩 Mensagem recebida de {From}: {Body}")

        # Processa mensagem com IA
        ai_response = await openai_service.process_message(Body)
        logger.info(f"🤖 Resposta da IA: {ai_response}")

        # Busca token do usuário no Supabase
        token = await supabase_client.get_calendar_token(From, provider="google")
        if not token:
            logger.warning("⚠️ Nenhum token encontrado")
            await twilio_service.send_message(
                From,
                f"📌 Para agendar eventos, preciso que você conecte seu Google Calendar.\n"
                f"Clique aqui para conectar: {os.getenv('BASE_URL')}/google/connect?user_phone={From}"
            )
            return {"status": "ok"}

        # Aqui você pode integrar com o Google Calendar
        await twilio_service.send_message(From, ai_response)

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        await twilio_service.send_message(From, "⚠️ Ocorreu um erro ao processar sua mensagem.")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/google/connect")
async def connect_google(user_phone: str):
    logger.info(f"🔗 Usuário {user_phone} acessou a página de conexão do Google.")
    return HTMLResponse(f"""
        <h3>Conectar Google Calendar</h3>
        <p>Usuário: {user_phone}</p>
        <p><a href='/google/oauth?user_phone={user_phone}'>Clique aqui para conectar seu Google Calendar</a></p>
    """)
