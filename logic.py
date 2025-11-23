import pandas as pd
import numpy as np

# ----------------------------------------------------------
# 1. Distribución horaria basada en registros reales
# ----------------------------------------------------------
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

    # suavizado para evitar ceros
    suav = 0.1
    conteos_suav = conteos + suav

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


# ----------------------------------------------------------
# 2. Pesos fijos por hora para predicción automática
# ----------------------------------------------------------
def pesos_horarios_pred():
    horas = pd.DataFrame({"hora": range(24)})
    horas["PESO_HORA"] = horas["hora"].apply(
        lambda h: 0.5 if h in range(0,6) else 
                  1.5 if h in range(6,12) else
                  2.5 if h in range(12,19) else
                  1.0
    )
    horas["p_hora"] = horas["PESO_HORA"] / horas["PESO_HORA"].sum()
    return horas
