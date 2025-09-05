import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def interpret_text(prompt: str) -> str:
    """
    Usa o modelo GPT para interpretar o texto recebido no WhatsApp.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente de calendário inteligente."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao interpretar com OpenAI: {e}"
