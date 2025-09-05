from openai import OpenAI
import os

# Inicializa o cliente usando a variável de ambiente OPENAI_API_KEY
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def interpret_text(prompt: str) -> str:
    """
    Interpreta o texto enviado pelo usuário (mensagem do WhatsApp).
    Usa o modelo GPT para entender a intenção e responder.
    """
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",  # Modelo rápido e barato
            messages=[
                {"role": "system", "content": "Você é um assistente de calendário integrado com WhatsApp."},
                {"role": "user", "content": prompt}
            ]
        )

        return resp.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ Erro ao processar com a IA: {str(e)}"
