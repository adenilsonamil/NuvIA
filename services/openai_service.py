import logging
import httpx
import os
from openai import AsyncOpenAI

logger = logging.getLogger("services.openai_service")

# Inicializa o cliente OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_chat_response(user_input: str) -> str:
    """
    Gera uma resposta da IA para um texto enviado pelo usuário.
    """
    try:
        logger.info(f"🤖 Enviando para GPT: {user_input}")

        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # modelo leve e rápido
            messages=[
                {"role": "system", "content": "Você é uma secretária pessoal que agenda reuniões e lembretes."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.6
        )

        reply = response.choices[0].message.content
        logger.info(f"🤖 Resposta da IA: {reply}")
        return reply

    except Exception as e:
        logger.error(f"❌ Erro GPT: {e}")
        return "⚠️ Ocorreu um erro ao processar sua mensagem com a IA."

async def transcribe_audio(audio_url: str) -> str:
    """
    Transcreve áudio do WhatsApp (URL) usando Whisper.
    """
    try:
        logger.info(f"🎤 Transcrevendo áudio de {audio_url}")

        async with httpx.AsyncClient() as client_http:
            audio_response = await client_http.get(audio_url)
            audio_bytes = audio_response.content

        transcript = await client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=("audio.ogg", audio_bytes, "audio/ogg")
        )

        text = transcript.text
        logger.info(f"📝 Transcrição concluída: {text}")
        return text

    except Exception as e:
        logger.error(f"❌ Erro ao transcrever áudio: {e}")
        return "⚠️ Não consegui transcrever seu áudio."
