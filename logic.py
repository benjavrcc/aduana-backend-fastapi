# daily_logic.py
import pandas as pd
from datetime import datetime, date
import calendar

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

    df["PESO"] = 1.0
    df.loc[df["ES_FINDE"], "PESO"] += 1.0
    df.loc[df["ES_FERIADO"], "PESO"] += 1.0
    df.loc[df["DIA_MES"] <= 5, "PESO"] += 0.5
    df.loc[df["DIA_MES"] >= 25, "PESO"] += 0.3

    total = df["PESO"].sum()
    df["p_dia"] = df["PESO"] / total

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
