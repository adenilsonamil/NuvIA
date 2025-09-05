import logging
import httpx
import os
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

logger = logging.getLogger("services.openai_service")

# Cliente assíncrono OpenAI
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def process_text_message(message: str) -> str:
    """
    Envia uma mensagem de texto para o modelo GPT e retorna a resposta.
    """
    logger.info(f"🤖 Enviando para GPT: {message}")
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # rápido e barato, pode trocar para "gpt-4o"
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é uma secretária pessoal inteligente e cordial. "
                        "Ajude o usuário a organizar reuniões, compromissos e lembretes. "
                        "Sempre confirme o que entendeu antes de registrar no calendário."
                    ),
                },
                {"role": "user", "content": message},
            ],
        )
        reply = response.choices[0].message.content
        logger.info(f"🤖 Resposta da IA: {reply}")
        return reply
    except Exception as e:
        logger.error(f"❌ Erro GPT: {e}")
        return "⚠️ Erro ao processar sua mensagem."


async def transcribe_audio(media_url: str) -> str | None:
    """
    Baixa um áudio do Twilio e envia para o Whisper (gpt-4o-transcribe).
    Retorna o texto transcrito ou None em caso de falha.
    """
    logger.info(f"🎙️ Transcrevendo áudio de {media_url}")
    try:
        async with httpx.AsyncClient() as client_http:
            audio = await client_http.get(media_url)
            audio.raise_for_status()
            audio_bytes = audio.content

        # salvar temporariamente
        temp_file = "temp_audio.ogg"
        with open(temp_file, "wb") as f:
            f.write(audio_bytes)

        # enviar para OpenAI Whisper
        with open(temp_file, "rb") as f:
            transcript = await client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=f,
            )

        os.remove(temp_file)  # limpar arquivo temporário
        logger.info(f"✅ Transcrição concluída: {transcript.text}")
        return transcript.text

    except Exception as e:
        logger.error(f"❌ Erro Whisper: {e}")
        return None
