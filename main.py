from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime

from models import Registro, DistribucionRequest
from logic import generar_distribucion_horaria, pesos_horarios_pred
from daily_logic import calcular_E_dia

MESES_ES = [
    "enero","febrero","marzo","abril","mayo","junio",
    "julio","agosto","septiembre","octubre","noviembre","diciembre"
]

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Memoria temporal solo para registros
registros_globales = []

@app.get("/")
def home():
    return {"mensaje": "Backend Aduana Digital funcionando 🔥"}


# -------------------------------------------
# 1) REGISTRAR VIAJERO
# -------------------------------------------
@app.post("/registrar")
def registrar(data: Registro):

    import os
    import pandas as pd

    os.makedirs("data", exist_ok=True)
    path = "data/registros.csv"

    # Si existe, agregar
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = pd.concat([df, pd.DataFrame([data.dict()])], ignore_index=True)
    else:
        df = pd.DataFrame([data.dict()])

    df.to_csv(path, index=False)

    return {
        "status": "ok",
        "mensaje": "Registro guardado",
        "total_registros": len(df)
    }


# -------------------------------------------
# 2) VER REGISTROS
# -------------------------------------------
@app.get("/registros")
def ver_registros():

    import os
    import pandas as pd

    path = "data/registros.csv"

    if not os.path.exists(path):
        return {"total_registros": 0, "registros": []}

    df = pd.read_csv(path)

    return {
        "total_registros": len(df),
        "registros": df.to_dict(orient="records")
    }


# -------------------------------------------
# 3) DISTRIBUCIÓN HORARIA CON REGISTROS REALES
# -------------------------------------------
@app.post("/distribucion")
def distribucion(req: DistribucionRequest):

    if len(registros_globales) == 0:
        return {"error": "No hay registros aún"}

    df = pd.DataFrame(registros_globales)
    resultado = generar_distribucion_horaria(df, req.esperado)

    return resultado.to_dict(orient="records")


# -------------------------------------------
# 4) PREDICCIÓN AUTOMÁTICA (USANDO CSV DEL 2025)
# -------------------------------------------
@app.get("/prediccion_horaria")
def prediccion_horaria(fecha: str = Query(..., description="YYYY-MM-DD")):
    import pandas as pd
    import os
    from datetime import datetime

    # ------------------------------
    # Validar fecha
    # ------------------------------
    try:
        f = datetime.strptime(fecha, "%Y-%m-%d").date()
    except:
        return {"error": "Formato inválido. Usa YYYY-MM-DD"}

    # ------------------------------
    # Mes en español
    # ------------------------------
    MESES_ES = [
        "enero","febrero","marzo","abril","mayo","junio",
        "julio","agosto","septiembre","octubre","noviembre","diciembre"
    ]
    mes_nombre = MESES_ES[f.month - 1]

    # ------------------------------
    # Leer predicciones CSV
    # ------------------------------
    path = "data/predicciones_2025.csv"

    if not os.path.exists(path):
        return {"error": "No existe predicciones_2025.csv en /data"}

    df = pd.read_csv(path)

    # Normalizar por seguridad
    df["MES"] = df["MES"].str.lower().str.strip()

    # Buscar predicción del mes
    fila = df[(df["MES"] == mes_nombre) & (df["ANIO"] == f.year)]

    if fila.empty:
        return {"error": f"No hay predicción disponible para {mes_nombre} {f.year}"}

    # E_mes (valor mensual predicho)
    E_mes = float(fila["PREDICCION"].iloc[0])

    # ------------------------------
    # Calcular E_dia (daily_logic)
    # ------------------------------
    from daily_logic import calcular_E_dia
    FERIADOS = [
        date(2025,1,1),
        date(2025,4,18),
        date(2025,5,1)
    ]

    E_dia, _ = calcular_E_dia(E_mes, fecha, FERIADOS)

    # ------------------------------
    # Distribución horaria
    # ------------------------------
    from logic import pesos_horarios_pred
    horas = pesos_horarios_pred()
    horas["pred_hora"] = E_dia * horas["p_hora"]

    # ------------------------------
    # Respuesta final JSON
    # ------------------------------
    return {
        "fecha": fecha,
        "mes": mes_nombre,
        "anio": f.year,
        "E_mes": round(E_mes),
        "E_dia": round(E_dia),
        "horas": horas.to_dict(orient="records")
    }
