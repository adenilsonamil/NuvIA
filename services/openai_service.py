import logging
import os
import aiohttp
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Cliente OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# URL base do Twilio para baixar mídia
TWILIO_MEDIA_BASE = "https://api.twilio.com"


async def process_message(user_message: str) -> str:
    """
    Processa uma mensagem de texto usando OpenAI e retorna uma resposta humanizada.
    """
    try:
        logger.info(f"🤖 Enviando mensagem para OpenAI: {user_message}")

        completion = await client.chat.completions.create(
            model="gpt-4o-mini",  # modelo leve e rápido
            messages=[
                {"role": "system", "content": "Você é uma secretária pessoal inteligente. \
Responda de forma natural, humanizada e fluida. Ajude o usuário a organizar reuniões, \
compromissos e lembretes. Sempre confirme horários de forma clara."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=300
        )

        reply = completion.choices[0].message.content.strip()
        logger.info(f"🤖 Resposta da IA: {reply}")
        return reply

    except Exception as e:
        logger.error(f"❌ Erro no OpenAI: {e}")
        return "⚠️ Desculpe, ocorreu um erro ao processar sua mensagem."


async def process_audio(media_url: str, auth: tuple) -> str:
    """
    Faz download de um áudio enviado via WhatsApp (Twilio) e converte em texto usando Whisper.
    
    :param media_url: URL do arquivo de áudio (fornecida pelo Twilio).
    :param auth: Tupla (account_sid, auth_token) para autenticação no Twilio.
    :return: Texto transcrito do áudio.
    """
    try:
        # 1. Baixar o áudio do Twilio
        logger.info(f"🎤 Baixando áudio de {media_url}")
        audio_bytes = None

        async with aiohttp.ClientSession() as session:
            async with session.get(media_url, auth=aiohttp.BasicAuth(*auth)) as resp:
                if resp.status == 200:
                    audio_bytes = await resp.read()
                else:
                    logger.error(f"❌ Erro ao baixar áudio: {resp.status}")
                    return "⚠️ Não consegui baixar o áudio."

        if not audio_bytes:
            return "⚠️ O áudio estava vazio ou não pôde ser baixado."

        # 2. Enviar para Whisper
        logger.info("🔎 Enviando áudio para transcrição (Whisper)...")
        transcription = await client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=("audio.ogg", audio_bytes)  # Twilio manda em OGG/AMR geralmente
        )

        text = transcription.text.strip()
        logger.info(f"📝 Transcrição concluída: {text}")
        return text

    except Exception as e:
        logger.error(f"❌ Erro ao processar áudio: {e}")
        return "⚠️ Não consegui transcrever o áudio."


