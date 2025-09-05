import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "SUA_CHAVE_OPENAI")

# Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "SEU_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "SEU_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "SUA_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "SUA_KEY")
