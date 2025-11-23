<<<<<<< HEAD
# logic.py
=======
# daily_logic.py
>>>>>>> f240e0f60d8e1d46cd933f231815e3c1629e11d6
import pandas as pd
from datetime import datetime, date
import calendar

<<<<<<< HEAD
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
=======
def pesos_diarios(year: int, month: int, feriados: list[date] = None):
    if feriados is None:
        feriados = []

    dias_mes = calendar.monthrange(year, month)[1]
    dias = pd.date_range(f"{year}-{month:02d}-01", periods=dias_mes)

    df = pd.DataFrame({"FECHA": dias})
    df["DIA_MES"] = df["FECHA"].dt.day
    df["DIA_SEM"] = df["FECHA"].dt.dayofweek
    df["ES_FINDE"] = df["DIA_SEM"].isin([5, 6])
    df["ES_FERIADO"] = df["FECHA"].dt.date.isin(feriados)
>>>>>>> f240e0f60d8e1d46cd933f231815e3c1629e11d6

    df["PESO"] = 1.0
    df.loc[df["ES_FINDE"], "PESO"] += 1.0
    df.loc[df["ES_FERIADO"], "PESO"] += 1.0
    df.loc[df["DIA_MES"] <= 5, "PESO"] += 0.5
    df.loc[df["DIA_MES"] >= 25, "PESO"] += 0.3

<<<<<<< HEAD
    # Predicción por hora
    pred = E * p_hora
=======
    total = df["PESO"].sum()
    df["p_dia"] = df["PESO"] / total
>>>>>>> f240e0f60d8e1d46cd933f231815e3c1629e11d6

    return df


def calcular_E_dia(E_mes: float, fecha_str: str, feriados: list[date] = None):
    f = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    df = pesos_diarios(f.year, f.month, feriados)

    row = df[df["FECHA"].dt.date == f]
    if len(row) == 0:
        raise ValueError(f"Fecha {fecha_str} fuera del mes válido.")

    p = float(row["p_dia"].iloc[0])
    E_dia = E_mes * p

    return E_dia, df

# Pesos fijos por hora (modelo horario)
import pandas as pd


# ----------------------------------------
# MODELO HORARIO (para predicción automática)
# ----------------------------------------
def pesos_horarios_pred():
    horas = pd.DataFrame({"hora": range(24)})
    horas["PESO_HORA"] = horas["hora"].apply(lambda h:
        0.5 if h in range(0,6) else
        1.5 if h in range(6,12) else
        2.5 if h in range(12,19) else
        1.0
    )
    horas["p_hora"] = horas["PESO_HORA"] / horas["PESO_HORA"].sum()
    return horas

<<<<<<< HEAD
    horas["PESO_HORA"] = horas["hora"].apply(lambda h:
        0.5 if h in range(0, 6) else      # madrugada
        1.5 if h in range(6, 12) else     # mañana
        2.5 if h in range(12, 19) else    # tarde alta
        1.0                                # noche
    )

    horas["p_hora"] = horas["PESO_HORA"] / horas["PESO_HORA"].sum()

    return horas
=======
>>>>>>> f240e0f60d8e1d46cd933f231815e3c1629e11d6
