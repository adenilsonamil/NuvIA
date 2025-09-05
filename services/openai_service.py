from openai import OpenAI
import logging
import os

logger = logging.getLogger("services.openai_service")

# Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🔹 Processar mensagens de texto
async def process_text_message(message: str) -> str:
    logger.info(f"🤖 Enviando para GPT: {message}")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Pode trocar por "gpt-4o" ou "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "Você é uma secretária pessoal que ajuda a organizar reuniões, compromissos e lembretes no calendário."},
                {"role": "user", "content": message}
            ],
        )
        reply = response.choices[0].message.content.strip()
        logger.info(f"🤖 Resposta da IA: {reply}")
        return reply
    except Exception as e:
        logger.error(f"❌ Erro GPT: {e}")
        return "⚠️ Não consegui processar sua mensagem."


# 🔹 Processar mensagens de áudio (voz → texto)
async def process_audio_message(audio_file_path: str) -> str:
    logger.info(f"🎙️ Transcrevendo áudio: {audio_file_path}")
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        text = transcript.text.strip()
        logger.info(f"🎙️ Transcrição: {text}")
        return text
    except Exception as e:
        logger.error(f"❌ Erro ao transcrever áudio: {e}")
        return "⚠️ Não consegui entender o áudio."
