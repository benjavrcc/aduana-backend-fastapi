import pandas as pd
import numpy as np

def generar_distribucion_horaria(df_registros, E):
    """
    df_registros: DataFrame con columnas:
        - fecha_llegada
        - hora_llegada
    E: cantidad esperada para ese día
    """

    df = df_registros.copy()
    df["hora"] = pd.to_datetime(df["hora_llegada"], format="%H:%M").dt.hour

    conteos = df.groupby("hora").size().reindex(range(24), fill_value=0)

    suavizado = 0.1
    conteos_suav = conteos + suavizado

    total = conteos_suav.sum()
    p_hora = conteos_suav / total

    pred = E * p_hora

    salida = pd.DataFrame({
        "hora": range(24),
        "conteo_real": conteos.values,
        "p_hora": p_hora.values,
        "pred_hora": pred.values
    })

    return salida
