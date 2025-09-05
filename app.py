from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from services import openai_service, twilio_service, google_calendar
from db import supabase_client
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "✅ NuvIA está rodando no Render!"}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Endpoint que o Twilio chama quando recebe uma mensagem no WhatsApp.
    """
    try:
        form = await request.form()
        sender = form.get("From")  # Número do usuário
        text = form.get("Body")    # Mensagem enviada

        if not text:
            return PlainTextResponse("⚠️ Nenhuma mensagem recebida.")

        print(f"📩 Mensagem recebida de {sender}: {text}")

        # Interpretação com OpenAI
        intent = openai_service.interpret_text(text)

        # Envia resposta ao usuário no WhatsApp
        twilio_service.send_message(sender, f"📌 Você disse: {text}\n🤖 Interpretei como: {intent}")

        return PlainTextResponse("ok")

    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return PlainTextResponse(f"Erro interno: {str(e)}", status_code=500)

@app.get("/google/callback")
async def google_callback(code: str):
    """
    Callback do Google OAuth2 para salvar tokens no Supabase.
    """
    try:
        tokens = google_calendar.exchange_code_for_tokens(code)
        supabase_client.save_calendar_tokens("google", tokens)
        return {"status": "ok", "message": "Google Calendar vinculado com sucesso ✅"}
    except Exception as e:
        print(f"❌ Erro no callback do Google: {e}")
        return {"status": "erro", "detalhe": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
