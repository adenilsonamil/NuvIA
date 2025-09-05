from fastapi import FastAPI, Request
from services import twilio_service, openai_service

app = FastAPI()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.form()
    user_message = data.get("Body", "")
    from_number = data.get("From", "")

    try:
        app.logger.info(f"📩 Mensagem recebida de {from_number}: {user_message}")

        # Extrair evento estruturado da IA
        event = await openai_service.get_event_from_text(user_message)

        if event and "titulo" in event:
            titulo = event.get("titulo")
            descricao = event.get("descricao", "")
            data_evento = event.get("data")
            hora_evento = event.get("hora")

            resumo = (
                f"✅ Evento criado com sucesso!\n\n"
                f"📌 *{titulo}*\n"
                f"📝 {descricao}\n"
                f"📅 {data_evento} às {hora_evento}"
            )

            # (futuramente: salvar em Supabase + criar no calendário real)
            await twilio_service.send_message(from_number, resumo)
        else:
            await twilio_service.send_message(from_number, "⚠️ Não consegui entender os detalhes do evento. Pode reformular?")

    except Exception as e:
        app.logger.error(f"❌ Erro no webhook: {e}")
        await twilio_service.send_message(from_number, "⚠️ Ocorreu um erro ao processar sua mensagem.")

    return {"status": "ok"}
