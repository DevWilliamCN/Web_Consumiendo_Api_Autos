import os
import streamlit as st
import requests
import pandas as pd
from recomendador import recomendar_autos

# URL de la API con los autos
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
        api_key = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY", None)
        if not api_key:
            return "❌ Falta configurar OPENROUTER_API_KEY en los secrets de Streamlit."

        # PROMPT MEJORADO
        prompt = f"""
Sos un asistente experto en autos. El usuario puede escribir de forma coloquial, profesional o en distintos idiomas.

Tu tarea es interpretar su intención y devolver exactamente uno de estos tres formatos en JSON:

1. Buscar por marca:
{{ "accion": "buscar", "params": {{ "marca": "Toyota" }} }}

2. Recomendación por preferencia:
{{ "accion": "preferencia", "preferencia": "económico" }}

3. Si no entendés:
{{ "accion": "desconocido" }}

---

Ejemplos de frases que indican una preferencia:
- "Quiero un carro barato"
- "Muéstrame los más nuevos"
- "Autos económicos"
- "Busco algo reciente y con buen rendimiento"
- "Una nave buena"
- "Quiero una nave"
- "Un carro que rinda bastante"
- "Busco un vehículo rendidor"
- "Muéstrame carros 2020 en adelante"
- "Recomendame algo potente pero económico"
- "Un auto bonito y rápido"
- "Algo cómodo y con poco consumo"

Frases multilingües que también podés entender:
- "Show me the cheapest cars"
- "I want a fuel-efficient car"
- "Voiture économique"
- "Quero um carro econômico"
- "Ich suche ein günstiges Auto"
- "Autos nuevos con buen puntaje"

Frase del usuario: "{pregunta_usuario}"
"""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "system", "content": "Respondé solamente con JSON válido según el formato especificado."},
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
            return f"❌ La respuesta del modelo no fue un JSON válido:\n\n{contenido}"

        df = cargar_datos()
        if df.empty:
            return "⚠️ No se pudieron cargar los datos de autos."

        if instruccion["accion"] == "buscar":
            marca = instruccion["params"].get("marca", "").strip()
            if not marca:
                return "⚠️ No se indicó una marca válida para buscar autos."
            filtrado = df[df["marca"].str.lower() == marca.lower()]
            if filtrado.empty:
                return f"⚠️ No se encontraron autos para la marca '{marca}'."
            return filtrado.head(5).to_markdown(index=False)

        if instruccion["accion"] == "preferencia":
            preferencia = instruccion.get("preferencia", "").strip()
            if not preferencia:
                return "⚠️ No se indicó una preferencia válida."
            recomendados = recomendar_autos(df, preferencia)
            if recomendados.empty:
                return f"⚠️ No se encontraron autos para la preferencia '{preferencia}'."
            return recomendados.to_markdown(index=False)

        return "🤖 No logré entender tu consulta."

    except Exception as e:
        return f"❌ Error inesperado: {e}"
