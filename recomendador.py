import pandas as pd

def recomendar_autos(df, preferencia):
    # Diccionario de estrategias según frase
    pesos = {
        "económico": {"precio": -0.5, "rendimiento_km_l": 1.0, "ranking": 0.5},
        "rendimiento": {"precio": -0.3, "rendimiento_km_l": 1.0, "ranking": 0.7},
        "mejor ranking": {"precio": -0.2, "rendimiento_km_l": 0.6, "ranking": 1.0},
        "equilibrado": {"precio": -0.3, "rendimiento_km_l": 0.7, "ranking": 0.7}
    }

    preferencia_lower = preferencia.lower()

    # Frases que indican interés en autos costosos
    frases_costosos = [
        "más caro", "carro más caro", "carros caros", "caro", "costoso", "carro costoso"
    ]

    # 1. Autos más caros por marca
    if "por marca" in preferencia_lower and any(frase in preferencia_lower for frase in frases_costosos):
        df_recientes = df[df["año"] >= 2022]
        recomendados = df_recientes.sort_values(by="precio", ascending=False)
        recomendados = (
            recomendados.groupby("marca")
            .first()
            .reset_index()
            .sort_values(by="precio", ascending=False)
            .head(5)
        )
        recomendados["puntaje"] = "💰 Más caro por marca"
        return recomendados[["marca", "modelo", "año", "precio", "rendimiento_km_l", "ranking", "puntaje"]]

    # 2. Solo autos recientes
    if "reciente" in preferencia_lower or "nuevo" in preferencia_lower:
        df = df[df["año"] >= 2022]

    # 3. Precio ajustado por rendimiento y ranking
    if "ajustado" in preferencia_lower:
        df = df.copy()
        df["precio_ajustado"] = df["precio"] / ((df["rendimiento_km_l"] + df["ranking"]) / 2)
        recomendados = df.sort_values(by="precio_ajustado").head(5)
        recomendados["puntaje"] = "📊 Precio ajustado por rendimiento y ranking"
        return recomendados[["marca", "modelo", "año", "precio", "rendimiento_km_l", "ranking", "precio_ajustado", "puntaje"]]

    # 4. Top más caros general
    if any(frase in preferencia_lower for frase in frases_costosos):
        recomendados = df.sort_values(by="precio", ascending=False).head(5)
        recomendados["puntaje"] = "💰 Top más caros"
        return recomendados[["marca", "modelo", "año", "precio", "rendimiento_km_l", "ranking", "puntaje"]]

    # 5. Recomendador basado en pesos (IA simple)
    clave = "equilibrado"
    for palabra in pesos.keys():
        if palabra in preferencia_lower:
            clave = palabra
            break

    p = pesos[clave]

    # Normalización de columnas
    df_norm = df.copy()
    for col in ["precio", "rendimiento_km_l", "ranking"]:
        df_norm[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

    # Cálculo del puntaje
    df["puntaje"] = (
        p["precio"] * df_norm["precio"] +
        p["rendimiento_km_l"] * df_norm["rendimiento_km_l"] +
        p["ranking"] * df_norm["ranking"]
    )

    recomendados = df.sort_values(by="puntaje", ascending=False).head(5)
    return recomendados[["marca", "modelo", "año", "precio", "rendimiento_km_l", "ranking", "puntaje"]]
