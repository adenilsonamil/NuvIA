import os
import logging
from openai import AsyncOpenAI

# Configuração do cliente OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def extract_meeting_info(user_message: str) -> dict:
    """
    Usa IA para interpretar mensagens do usuário e extrair dados da reunião.
    Retorna um dicionário com:
      - titulo
      - data_hora (ISO 8601 ou descrição compreensível)
      - local
      - notas
    """
    try:
        logger.info(f"🔎 Extraindo informações da mensagem: {user_message}")

        prompt = f"""
Você é uma secretária virtual inteligente. 
O usuário vai enviar mensagens em português solicitando agendamento de reuniões.

Sua tarefa é extrair os seguintes campos e retornar em JSON:
- titulo: título da reunião (se não houver, use "Reunião")
- data_hora: data e hora da reunião (em formato ISO 8601 se possível, ou texto compreensível como 'amanhã às 14h')
- local: local da reunião (se não informado, deixe vazio)
- notas: observações adicionais, como nomes de participantes ou tema (se não houver, deixe vazio)

Exemplo:
Entrada: "Agende uma reunião com João amanhã às 14h no escritório sobre o projeto X"
Saída:
{{
  "titulo": "Reunião sobre o projeto X",
  "data_hora": "amanhã às 14h",
  "local": "escritório",
  "notas": "Participante: João"
}}

Agora processe a mensagem do usuário:
"{user_message}"
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é uma assistente experiente em organizar compromissos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()

        # Tentativa de converter em dict
        import json
        meeting_info = json.loads(content)

        logger.info(f"✅ Extraído: {meeting_info}")
        return meeting_info

    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem com IA: {e}")
        return {}
