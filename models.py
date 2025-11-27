from pydantic import BaseModel

class Registro(BaseModel):
    fecha_llegada: str
    hora_llegada: str
    cantidad_viajeros: int

class DistribucionRequest(BaseModel):
    esperado: float
