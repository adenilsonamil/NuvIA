import openai
import requests
import config

openai.api_key = config.OPENAI_API_KEY

def transcribe_audio(media_url):
    audio = requests.get(media_url).content
    transcript = openai.Audio.transcriptions.create(
        model="whisper-1",
        file=("audio.ogg", audio)
    )
    return transcript["text"]

def interpret_text(text):
    prompt = f"""
    Interprete o texto a seguir como uma intenção de calendário.
    Retorne em JSON válido com: action(create|update|delete|list),
    title, datetime (YYYY-MM-DD HH:MM), calendar (google|outlook|apple).

    Texto: "{text}"
    """

    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Você é um assistente de calendário."},
                  {"role": "user", "content": prompt}]
    )

    import json
    try:
        return json.loads(resp["choices"][0]["message"]["content"])
    except:
        return {"action": "none"}
