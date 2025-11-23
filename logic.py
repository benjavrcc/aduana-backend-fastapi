import pandas as pd
import numpy as np

def generar_distribucion_horaria(df_registros, E):
   
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

def pesos_horarios_pred():
    horas = pd.DataFrame({"hora": range(24)})

    def peso(h):
        if 0 <= h <= 5: return 0.5
        if 6 <= h <= 11: return 1.5
        if 12 <= h <= 18: return 2.5
        return 1.0

    horas["peso"] = horas["hora"].apply(peso)
    horas["p_hora"] = horas["peso"] / horas["peso"].sum()

    return horas