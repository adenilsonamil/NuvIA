import openai
import logging
import httpx
from config import OPENAI_API_KEY

logger = logging.getLogger("services.openai_service")
openai.api_key = OPENAI_API_KEY


async def process_text_message(message: str) -> str:
    logger.info(f"🤖 Enviando para GPT: {message}")
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é uma secretária pessoal que ajuda com calendários e lembretes."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        logger.error(f"❌ Erro GPT: {e}")
        return "⚠️ Erro ao processar sua mensagem."


async def transcribe_audio(media_url: str) -> str:
    logger.info(f"🎙️ Transcrevendo áudio de {media_url}")
    try:
        async with httpx.AsyncClient() as client:
            audio = await client.get(media_url)
            audio_bytes = audio.content

        transcript = await openai.Audio.atranscribe(
            "whisper-1",
            file=("audio.ogg", audio_bytes, "audio/ogg")
        )
        return transcript["text"]
    except Exception as e:
        logger.error(f"❌ Erro Whisper: {e}")
        return None
