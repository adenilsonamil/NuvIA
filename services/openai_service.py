import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def interpret_text(user_message: str) -> dict:
    """
    Interpreta a intenção do usuário (reunião, lembrete, outro).
    Retorna um dicionário estruturado.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é uma secretária pessoal inteligente. "
                        "Sua função é interpretar mensagens em português e classificá-las em: "
                        "1) 'reuniao' → quando o usuário pede para agendar reunião. "
                        "2) 'lembrete' → quando o usuário pede para ser lembrado de algo. "
                        "3) 'outro' → qualquer coisa diferente. "
                        "Sempre extraia data, hora e descrição quando possível."
                    )
                },
                {"role": "user", "content": user_message}
            ],
            temperature=0.3
        )

        content = response.choices[0].message.content.strip()

        # Força o retorno em JSON (tratamento de exceções)
        import json
        try:
            data = json.loads(content)
        except Exception:
            data = {"intent": "outro", "text": content}

        return data

    except Exception as e:
        return {"intent": "erro", "text": f"⚠️ Erro na interpretação: {str(e)}"}
