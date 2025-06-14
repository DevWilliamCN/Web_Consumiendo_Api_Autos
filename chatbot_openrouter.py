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
            return "\u274c Falta configurar OPENROUTER_API_KEY en los secrets de Streamlit."

        prompt = f"""
Sos un asistente inteligente experto en autos. El usuario puede escribir frases como:
- \"Quiero un carro barato\"
- \"Un auto que rinda bastante\"
- \"Mu\u00e9strame los m\u00e1s nuevos\"
- \"Cu\u00e1l es el carro m\u00e1s caro\"
- \"Busco algo reciente y con buen rendimiento\"
- \"Un veh\u00edculo que sea rendidor y econ\u00f3mico\"
- \"Recomendame una marca buena\"
- \"Busco carro familiar que no gaste mucha gasolina\"
- \"Quiero una nave que consuma poco\"
- \"Necesito algo confiable y que no gaste tanto\"
- \"Mu\u00e9strame autos 2020 en adelante\"

Tambi\u00e9n puede usar otros idiomas como:
- \"Show me the cheapest cars\"
- \"I want a fuel-efficient car\"
- \"Voiture \u00e9conomique\"
- \"Quero um carro econ\u00f4mico\"
- \"Ich suche ein g\u00fcnstiges Auto\"

Interpret\u00e1 la intenci\u00f3n y devolv\u00e9 SOLO un JSON con una de estas estructuras:

1. Buscar por marca:
{{ "accion": "buscar", "params": {{ "marca": "Toyota" }} }}

2. Recomendaci\u00f3n por preferencia:
{{ "accion": "preferencia", "preferencia": "econ\u00f3mico" }}

3. Si no entend\u00e9s:
{{ "accion": "desconocido" }}

Frase del usuario: \"{pregunta_usuario}\"
"""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "system", "content": "Respond\u00e9 solamente con JSON v\u00e1lido seg\u00fan el formato especificado."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        data = response.json()

        if response.status_code != 200 or "choices" not in data:
            msg = data.get("error", {}).get("message", "Respuesta inv\u00e1lida")
            return f"\u274c Error {response.status_code}: {msg}"

        contenido = data["choices"][0]["message"]["content"].strip()

        try:
            instruccion = eval(contenido)
        except:
            return f"\u274c La respuesta del modelo no fue un JSON v\u00e1lido:\n\n{contenido}"

        df = cargar_datos()
        if df.empty:
            return "\u26a0\ufe0f No se pudieron cargar los datos de autos."

        if instruccion["accion"] == "buscar":
            marca = instruccion["params"].get("marca", "").strip()
            if not marca:
                return "\u26a0\ufe0f No se indic\u00f3 una marca v\u00e1lida para buscar autos."
            filtrado = df[df["marca"].str.lower() == marca.lower()]
            if filtrado.empty:
                return f"\u26a0\ufe0f No se encontraron autos para la marca '{marca}'."
            return filtrado.head(5).to_markdown(index=False)

        if instruccion["accion"] == "preferencia":
            preferencia = instruccion.get("preferencia", "").strip()
            if not preferencia:
                return "\u26a0\ufe0f No se indic\u00f3 una preferencia v\u00e1lida."
            recomendados = recomendar_autos(df, preferencia)
            if recomendados.empty:
                return f"\u26a0\ufe0f No se encontraron autos para la preferencia '{preferencia}'."
            return recomendados.to_markdown(index=False)

        return "\ud83e\udd16 No logre entender tu consulta."

    except Exception as e:
        return f"\u274c Error inesperado: {e}"
