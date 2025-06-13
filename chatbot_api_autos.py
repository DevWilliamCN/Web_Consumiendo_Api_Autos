import openai
import os
from dotenv import load_dotenv
import requests
import pandas as pd

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

BASE_URL = "https://api-william.datapiwilliam.workers.dev/api/autos"

def consultar_api(params=None):
    try:
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def chatbot_ia(pregunta_usuario):
    prompt = f"""
Actúa como un asistente experto en autos de Costa Rica. Analiza esta pregunta:

{pregunta_usuario}

Y responde usando solo este formato:
{{ "accion": "buscar", "params": {{ "marca": "Kia" }} }}
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres experto en APIs de autos y debes responder con JSON estructurado para que yo lo use directamente."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content
        resultado = eval(content.strip())

        if resultado.get("accion") == "buscar":
            df = consultar_api(resultado.get("params"))
            if df.empty:
                return "⚠️ No se encontraron autos con esos filtros."
            return df.to_markdown(index=False)

        return "🤖 No entendí tu consulta."

    except Exception as e:
        return f"❌ Error: {e}"
