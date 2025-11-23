# daily_logic.py
import pandas as pd
from datetime import datetime, date
import calendar

def pesos_diarios(year: int, month: int, feriados: list[date] = None):
    """
    Crea la distribución de pesos para cada día de un mes.
    - Penaliza o potencia según:
        * fin de semana
        * primeros 5 días
        * últimos días del mes
        * feriados (si se entregan)
    """
    if feriados is None:
        feriados = []

    # Cuántos días tiene el mes
    dias_mes = calendar.monthrange(year, month)[1]

    # Rango de fechas del mes
    dias = pd.date_range(f"{year}-{month:02d}-01", periods=dias_mes)

    df = pd.DataFrame({"FECHA": dias})
    df["DIA_MES"] = df["FECHA"].dt.day
    df["DIA_SEM"] = df["FECHA"].dt.dayofweek  # 0=lunes … 6=domingo

    # ¿Es fin de semana?
    df["ES_FINDE"] = df["DIA_SEM"].isin([5, 6])

    # ¿Es feriado?
    df["ES_FERIADO"] = df["FECHA"].dt.date.isin(feriados)

    # Pesos base + ajustes
    df["PESO"] = 1.0
    df.loc[df["ES_FINDE"], "PESO"] += 1.0       # finde pesa más
    df.loc[df["ES_FERIADO"], "PESO"] += 1.0      # feriado pesa aún más
    df.loc[df["DIA_MES"] <= 5, "PESO"] += 0.5    # primeros días más fuertes
    df.loc[df["DIA_MES"] >= 25, "PESO"] += 0.3   # últimos días también

    # Probabilidad diaria
    total = df["PESO"].sum()
    df["p_dia"] = df["PESO"] / total

    return df


def calcular_E_dia(E_mes: float, fecha_str: str, feriados: list[date] = None):
    """
    Dado E_mes (predicción mensual) y una fecha específica:
    → calcula E_dia usando pesos diarios.
    """
    f = datetime.strptime(fecha_str, "%Y-%m-%d").date()

    df = pesos_diarios(f.year, f.month, feriados)

    # Extraer el peso del día exacto
    row = df[df["FECHA"].dt.date == f]
    if len(row) == 0:
        raise ValueError(f"Fecha {fecha_str} fuera del mes válido.")

    p = float(row["p_dia"].iloc[0])
    E_dia = E_mes * p

    return E_dia, df
