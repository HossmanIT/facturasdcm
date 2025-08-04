from pydantic import BaseModel
from datetime import datetime

class Factura(BaseModel):
    CVE_DOC: str
    NOMBRE: str
    CVE_PEDI: str
    FECHA_DOC: datetime
    FECHA_VEN: datetime
    MONEDA: str
    TIPCAMB: float
    IMPORTE: float
    IMPORTEME: float
    VENDEDOR: str
    SINCRONIZADO: bool

class MondayItem(BaseModel):
    name: str
    column_values: dict