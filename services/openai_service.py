import openai
import logging
import os

logger = logging.getLogger("services.openai_service")

openai.api_key = os.getenv("OPENAI_API_KEY")

async def process_text_message(message: str) -> str:
    logger.info(f"🤖 Enviando para GPT: {message}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é uma secretária pessoal que ajuda com calendário e lembretes."},
                {"role": "user", "content": message}
            ],
        )
        reply = response["choices"][0]["message"]["content"].strip()
        return reply
    except Exception as e:
        logger.error(f"❌ Erro GPT: {e}")
        return "⚠️ Não consegui processar sua mensagem."
