from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Lo que recibimos del ESP32
class BasculaLectura(BaseModel):
    id: int
    peso: float
    status: str

class TelemetriaPayload(BaseModel):
    temp_camara: float
    basculas: List[BasculaLectura]
    uptime_ms: int

# Estructura del Recetario
class IngredienteReceta(BaseModel):
    id_sensor: int
    gramos_necesarios: float

class Receta(BaseModel):
    nombre_plato: str
    precio_venta: float
    ingredientes: List[IngredienteReceta]