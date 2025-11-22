from fastapi import FastAPI
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
from models import Registro, DistribucionRequest
from logic import generar_distribucion_horaria
import pandas as pd

# Permite que tu web en Vercel llame al backend sin bloqueo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# ALMACEN TEMPORAL (MEMORIA)
# ----------------------------
registros_globales = []

@app.get("/")
def home():
    return {"mensaje": "Backend FastAPI funcional compa 🔥"}

# ----------------------------
# REGISTRAR VIAJE
# ----------------------------
@app.post("/registrar")
def registrar(data: Registro):
    registros_globales.append(data.dict())
    return {"status": "ok", "mensaje": "Registro guardado", "total_registros": len(registros_globales)}

# ----------------------------
# DISTRIBUCIÓN HORARIA
# ----------------------------
@app.post("/distribucion")
def distribucion(req: DistribucionRequest):

    if len(registros_globales) == 0:
        return {"error": "No hay registros en memoria todavía"}

    df = pd.DataFrame(registros_globales)
    resultado = generar_distribucion_horaria(df, req.esperado)

    return resultado.to_dict(orient="records")
