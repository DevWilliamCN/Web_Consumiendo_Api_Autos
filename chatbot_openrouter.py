import os
import requests
import pandas as pd
import json
from recomendador import recomendar_autos

API_KEY = "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"
BASE_URL = "https://api-william.datapiwilliam.workers.dev/api/autos"

def cargar_datos():
    try:
        r = requests.get(BASE_URL)
        if r.status_code == 200:
            return pd.DataFrame(r.json())
        return pd.DataFrame()
    except:
        return pd.DataFrame()

def chatbot_ia(pregunta_usuario):
    try:
        prompt = f"""
Sos un asistente experto en autos. Con esta pregunta del usuario:

\"{pregunta_usuario}\"

respondé solamente con una de estas instrucciones en formato JSON:

1. Buscar por marca:
{{ "accion": "buscar", "params": {{ "marca": "Toyota" }} }}

2. Recomendación por preferencia:
{{ "accion": "preferencia", "preferencia": "económico" }}

3. Si no entendés:
{{ "accion": "desconocido" }}
"""

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "system", "content": "Respondé con JSON válido según lo solicitado."},
                {"role": "user", "content": prompt}
            ]
        }

        res = requests.post(url, json=body, headers=headers)
        contenido = res.json()["choices"][0]["message"]["content"].strip()

        instruccion = json.loads(contenido)
        df = cargar_datos()

        if df.empty:
            return "❌ No se pudieron cargar los datos."

        if instruccion["accion"] == "buscar":
            marca = instruccion["params"]["marca"]
            filtrado = df[df["marca"].str.lower() == marca.lower()]
            if filtrado.empty:
                return "⚠️ No se encontraron autos para esa marca."
            return filtrado.head(5).to_markdown(index=False)

        if instruccion["accion"] == "preferencia":
            preferencia = instruccion["preferencia"]
            recomendados = recomendar_autos(df, preferencia)
            return recomendados.to_markdown(index=False)

        return "🤖 No logré entender tu consulta."

    except Exception as e:
        return f"❌ Error: {e}"
