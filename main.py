from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime, date

# ---- Modelos propios ----
from models import Registro, DistribucionRequest
from logic import generar_distribucion_horaria, pesos_horarios_pred
from model_monthly import PredictorMensual, MESES
from daily_logic import calcular_E_dia

app = FastAPI()

# Instancia del modelo NB
pred = PredictorMensual()

# Permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Memoria temporal para los viajeros registrados
registros_globales = []


# -------------------------------------------------------------------
# HOME
# -------------------------------------------------------------------
@app.get("/")
def home():
    return {"mensaje": "Backend FastAPI funcional compa 🔥"}


# -------------------------------------------------------------------
# REGISTRAR VIAJE
# -------------------------------------------------------------------
@app.post("/registrar")
def registrar(data: Registro):
    registros_globales.append(data.dict())
    return {
        "status": "ok",
        "mensaje": "Registro guardado",
        "total_registros": len(registros_globales)
    }


# -------------------------------------------------------------------
# VER REGISTROS GUARDADOS
# -------------------------------------------------------------------
@app.get("/registros")
def ver_registros():
    return {
        "total_registros": len(registros_globales),
        "registros": registros_globales
    }


# -------------------------------------------------------------------
# DISTRIBUCIÓN HORARIA BASADA EN REGISTROS REALES
# -------------------------------------------------------------------
@app.post("/distribucion")
def distribucion(req: DistribucionRequest):

    if len(registros_globales) == 0:
        return {"error": "No hay registros en memoria todavía"}

    df = pd.DataFrame(registros_globales)
    resultado = generar_distribucion_horaria(df, req.esperado)

    return resultado.to_dict(orient="records")


# -------------------------------------------------------------------
# NUEVO: PREDICCIÓN AUTOMÁTICA POR HORA (MODELO MENSUAL + DIARIO + HORARIO)
# -------------------------------------------------------------------
FERIADOS = [
    date(2025,1,1),
    date(2025,4,18),
    date(2025,5,1)
]

@app.get("/prediccion_horaria")
def prediccion_horaria(fecha: str = Query(..., description="YYYY-MM-DD")):

    try:
        f = datetime.strptime(fecha, "%Y-%m-%d").date()
    except:
        return {"error": "Formato de fecha inválido. Usa YYYY-MM-DD"}

    mes_nombre = MESES[f.month - 1]

    # 1) Predicción mensual E_mes
    E_mes = pred.predict_month_total(mes_nombre, f.year)

    # 2) Predicción diaria E_dia
    E_dia, _tabla = calcular_E_dia(E_mes, fecha, FERIADOS)

    # 3) Distribución horaria automática
    horas = pesos_horarios_pred()
    horas["pred_hora"] = E_dia * horas["p_hora"]

    return {
        "fecha": fecha,
        "mes": mes_nombre,
        "anio": f.year,
        "E_mes": round(E_mes),
        "E_dia": round(E_dia),
        "horas": horas.to_dict(orient="records")
    }


# -------------------------------------------------------------------
# ENDPOINT PARA GUARDAR ECONOMÍA (APPEND-ONLY)
# -------------------------------------------------------------------
from pydantic import BaseModel

class EconomiaIn(BaseModel):
    anio: int
    mes: str
    clp_usd: float
    ars_usd: float
    ipc_cl: float
    ipc_ar: float


@app.post("/economia")
def guardar_economia(data: EconomiaIn):
    import os

    path = "data/economia.csv"
    os.makedirs("data", exist_ok=True)

    # Cargar si existe o crear
    if os.path.exists(path):
        df = pd.read_csv(path)
    else:
        df = pd.DataFrame(columns=["ANIO","MES","CLP_USD","ARS_USD","IPC_CL","IPC_AR","TCR"])

    # Calcular TCR
    tcn = data.clp_usd / data.ars_usd
    tcr = tcn * (data.ipc_ar / data.ipc_cl)

    nueva = pd.DataFrame([{
        "ANIO": data.anio,
        "MES": data.mes.lower(),
        "CLP_USD": data.clp_usd,
        "ARS_USD": data.ars_usd,
        "IPC_CL": data.ipc_cl,
        "IPC_AR": data.ipc_ar,
        "TCR": tcr
    }])

    df = pd.concat([df, nueva], ignore_index=True)
    df.to_csv(path, index=False)

    return {"ok": True, "tcr": tcr, "total_registros": len(df)}


@app.get("/economia")
def ver_economia():
    import os
    path = "data/economia.csv"
    if not os.path.exists(path):
        return []
    return pd.read_csv(path).to_dict(orient="records")
