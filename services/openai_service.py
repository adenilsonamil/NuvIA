import logging
import httpx
import os
from openai import AsyncOpenAI

logger = logging.getLogger("services.openai_service")
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def transcribe_audio(audio_url: str) -> str:
    """Transcreve áudio usando Whisper API."""
    async with httpx.AsyncClient() as http_client:
        audio = await http_client.get(audio_url)
        with open("temp_audio.ogg", "wb") as f:
            f.write(audio.content)

    with open("temp_audio.ogg", "rb") as f:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return transcript.text

async def extract_meeting_info(user_message: str) -> dict:
    """Usa ChatGPT para extrair infos de reunião."""
    logger.info(f"🔎 Extraindo informações da mensagem: {user_message}")

    prompt = f"""
    Extraia as informações de agendamento da mensagem abaixo e devolva em JSON.
    Se algo não for encontrado, deixe vazio.

    Mensagem: "{user_message}"

    JSON esperado:
    {{
        "titulo": "...",
        "data_hora": "...",
        "local": "...",
        "notas": "..."
    }}
    """

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Você é uma secretária pessoal."},
                  {"role": "user", "content": prompt}]
    )

    try:
        return eval(response.choices[0].message.content)
    except Exception:
        return {"titulo": "Reunião", "data_hora": "", "local": "", "notas": ""}
