from pydantic import BaseModel

class Registro(BaseModel):
    fecha_llegada: str
    hora_llegada: str

class DistribucionRequest(BaseModel):
    registros: list[Registro]
    esperado: float
