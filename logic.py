# logic.py
import pandas as pd
import numpy as np

# ----------------------------------------
# DISTRIBUCIÓN REAL BASADA EN REGISTROS
# ----------------------------------------
def generar_distribucion_horaria(df_registros, E):
    """
    df_registros: DataFrame con columnas:
        - fecha_llegada
        - hora_llegada
    E: cantidad esperada para ese día
    """

    df = df_registros.copy()
    df["hora"] = pd.to_datetime(df["hora_llegada"], format="%H:%M").dt.hour

    # Conteo real por hora
    conteos = df.groupby("hora").size().reindex(range(24), fill_value=0)

    # Suavizado (para evitar ceros)
    suavizado = 0.1
    conteos_suav = conteos + suavizado

    total = conteos_suav.sum()
    p_hora = conteos_suav / total

    # Predicción por hora
    pred = E * p_hora

    salida = pd.DataFrame({
        "hora": range(24),
        "conteo_real": conteos.values,
        "p_hora": p_hora.values,
        "pred_hora": pred.values
    })

    return salida


# ----------------------------------------
# MODELO HORARIO (para predicción automática)
# ----------------------------------------
def pesos_horarios_pred():
    horas = pd.DataFrame({"hora": range(24)})

    horas["PESO_HORA"] = horas["hora"].apply(lambda h:
        0.5 if h in range(0, 6) else      # madrugada
        1.5 if h in range(6, 12) else     # mañana
        2.5 if h in range(12, 19) else    # tarde alta
        1.0                                # noche
    )

    horas["p_hora"] = horas["PESO_HORA"] / horas["PESO_HORA"].sum()

    return horas
