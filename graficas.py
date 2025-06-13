import streamlit as st
import pandas as pd
import plotly.express as px
import requests

BASE_URL = "https://api-william.datapiwilliam.workers.dev"

def cargar_datos(params):
    response = requests.get(f"{BASE_URL}/api/autos", params=params)
    autos = response.json()
    if isinstance(autos, list) and autos:
        return pd.DataFrame(autos)
    else:
        return pd.DataFrame()

def mostrar_graficas(df):
    st.subheader("📊 Precio promedio por categoría")
    avg_price = df.groupby("categoria")["precio"].mean().reset_index()
    fig = px.bar(avg_price, x="categoria", y="precio", title="Precio Promedio por Categoría", color="categoria")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Rendimiento promedio por marca")
    avg_rend = df.groupby("marca")["rendimiento_km_l"].mean().reset_index()
    fig2 = px.line(avg_rend, x="marca", y="rendimiento_km_l", title="Rendimiento Promedio por Marca", markers=True)
    st.plotly_chart(fig2, use_container_width=True)
