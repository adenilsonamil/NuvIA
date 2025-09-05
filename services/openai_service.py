import os
import logging
from openai import OpenAI

logger = logging.getLogger("services.openai_service")

# Inicializa cliente OpenAI com a chave da API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def process_text_message(message: str) -> str:
    """
    Processa uma mensagem de texto com o modelo GPT.
    Retorna a resposta gerada ou mensagem de erro.
    """
    try:
        logger.info(f"🤖 Enviando para GPT: {message}")

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # modelo rápido e barato
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é uma secretária pessoal chamada Nuvia. "
                        "Sua função é organizar compromissos, criar lembretes "
                        "e responder de forma simpática e profissional."
                    ),
                },
                {"role": "user", "content": message},
            ],
        )

        reply = response.choices[0].message.content.strip()
        logger.info(f"🤖 Resposta da IA: {reply}")
        return reply

    except Exception as e:
        logger.error(f"❌ Erro GPT: {e}")
        return "⚠️ Desculpe, ocorreu um erro ao processar sua mensagem."


async def process_audio_message(audio_text: str) -> str:
    """
    Processa mensagens de áudio transcritas.
    O parâmetro recebido já deve ser o texto da transcrição.
    """
    return await process_text_message(audio_text)
