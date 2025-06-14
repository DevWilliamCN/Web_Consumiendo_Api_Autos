import os
import requests
import pandas as pd
from recomendador import recomendar_autos

# API externa con datos de autos
BASE_URL = "https://api-william.datapiwilliam.workers.dev/api/autos"

def cargar_datos():
    try:
        r = requests.get(BASE_URL)
        if r.status_code == 200:
            return pd.DataFrame(r.json())
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# Chatbot con integración a OpenRouter
def chatbot_ia(pregunta_usuario):
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return "❌ Falta configurar OPENROUTER_API_KEY en los secrets de Streamlit."

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

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

        body = {
            "model": "mistralai/mistral-7b-instruct:free",  # Gratis
            "messages": [
                {"role": "system", "content": "Respondé con JSON válido según lo solicitado."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        data = response.json()

        if response.status_code != 200 or "choices" not in data:
            msg = data.get("error", {}).get("message", "Respuesta inválida")
            return f"❌ Error {response.status_code}: {msg}"

        contenido = data["choices"][0]["message"]["content"].strip()

        try:
            instruccion = eval(contenido)
        except:
            return f"❌ La respuesta no fue un JSON válido:\n\n{contenido}"

        df = cargar_datos()
        if df.empty:
            return "⚠️ No se pudieron cargar los datos de autos."

        if instruccion["accion"] == "buscar":
            marca = instruccion["params"].get("marca", "")
            filtrado = df[df["marca"].str.lower() == marca.lower()]
            if filtrado.empty:
                return f"⚠️ No se encontraron autos para la marca '{marca}'."
            return filtrado.head(5).to_markdown(index=False)

        if instruccion["accion"] == "preferencia":
            preferencia = instruccion["preferencia"]
            recomendados = recomendar_autos(df, preferencia)
            return recomendados.to_markdown(index=False)

        return "🤖 No logré entender tu consulta."

    except Exception as e:
        return f"❌ Error inesperado: {e}"
