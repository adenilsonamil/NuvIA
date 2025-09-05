import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_event_from_text(user_message: str) -> dict:
    """
    Interpreta a mensagem do usuário e retorna um evento estruturado em JSON.
    """
    try:
        logger.info(f"🤖 Enviando para GPT (extração de evento): {user_message}")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é uma secretária pessoal. "
                        "Sempre extraia as informações de agendamento e retorne em JSON com os campos: "
                        "titulo, descricao, data (AAAA-MM-DD), hora (HH:MM no formato 24h). "
                        "Se faltar algum dado, deduza ou deixe vazio."
                    )
                },
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"}
        )

        event = response.choices[0].message.content
        logger.info(f"🤖 JSON estruturado retornado: {event}")
        return eval(event)  # transforma string JSON em dict

    except Exception as e:
        logger.error(f"❌ Erro GPT: {e}")
        return {}
