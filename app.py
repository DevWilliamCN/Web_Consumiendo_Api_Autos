import streamlit as st
import io
import pandas as pd

from graficas import cargar_datos, mostrar_graficas
from recomendador import recomendar_autos
from chatbot_openrouter import chatbot_ia  # ✅ Usamos IA real de OpenRouter

# Configuración de página
st.set_page_config(page_title="API de Autos CR", layout="wide")
st.title("🚗 Análisis de Automóviles en Costa Rica")

# Filtros de búsqueda
st.sidebar.header("🔎 Filtros")
marca = st.sidebar.text_input("Marca (ej: Toyota)")
categoria = st.sidebar.text_input("Categoría (ej: SUV)")

params = {}
if marca:
    params["marca"] = marca
if categoria:
    params["categoria"] = categoria

# Cargar datos desde la API
st.subheader("📋 Datos de automóviles")
df = cargar_datos(params)

if not df.empty:
    st.dataframe(df)

    # Gráficas interactivas
    mostrar_graficas(df)

    # Recomendador inteligente
    st.subheader("🔮 Recomendador inteligente de autos")

    with st.expander("🧠 Cómo escribir tu búsqueda", expanded=True):
        st.markdown("""
        Puedes escribir de forma **natural y sin restricciones**, por ejemplo:

        - **"Quiero un auto económico"**  
        - **"Busco un carro con buen rendimiento"**  
        - **"Muéstrame el más caro"**  
        - **"Quiero el carro más caro por marca"**  
        - **"Quiero un auto nuevo o reciente"**  
        - **"Carro con precio ajustado al rendimiento"**  
        - **"Recomendame algo bueno"**  
        - **"Autos nuevos con buena puntuación"**

        🔎 La inteligencia artificial interpretará tu frase y mostrará los autos recomendados según tu intención.
        """)

    preferencia = st.text_input(
        "✍️ Escribe aquí lo que buscas en un auto",
        placeholder="Ej: económico, más caro, por marca, rendimiento..."
    )

    if preferencia:
        recomendados = recomendar_autos(df, preferencia)
        st.markdown("### 🚘 Autos recomendados para ti:")
        st.dataframe(recomendados)

        # Botón para descargar recomendaciones como Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            recomendados.to_excel(writer, index=False, sheet_name='Recomendados')
        st.download_button(
            label="📥 Descargar recomendados en Excel",
            data=buffer,
            file_name="recomendados_autos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Chat con IA (OpenRouter)
    st.subheader("💬 Chat de consulta con IA sobre autos")
    pregunta = st.text_input("Haz tu pregunta:", placeholder="Ej: ¿Qué autos hay de la marca Honda?")

    if pregunta:
        respuesta = chatbot_ia(pregunta)
        st.markdown("**📬 Respuesta del asistente:**")

        try:
            # Si es tabla markdown, mostrar como DataFrame
            if respuesta.strip().startswith("|"):
                import io
                df_respuesta = pd.read_csv(io.StringIO(respuesta), sep="|", engine="python", skipinitialspace=True)
                df_respuesta = df_respuesta.dropna(axis=1, how="all")  # Eliminar columnas vacías
                st.dataframe(df_respuesta)
            else:
                st.markdown(f"📢 {respuesta}")
        except Exception as e:
            st.error(f"❌ Error al mostrar respuesta: {e}")
            st.text(respuesta)

else:
    st.warning("⚠️ No se encontraron autos con esos filtros.")

st.caption("📡 Datos en tiempo real desde la API pública de William Cubero")
