from sqlalchemy import Column, String, String, String, DateTime, DateTime, String, Float, Float, Float, String, Boolean
from core.database import Base

class SQLFACTF02(Base):
    __tablename__ = "SQLFACTF02"
    
    CVE_DOC = Column(String, primary_key=True)
    NOMBRE = Column(String)
    CVE_PEDI = Column(String)
    FECHA_DOC = Column(DateTime)
    FECHA_VEN = Column(DateTime)
    MONEDA = Column(String)
    TIPCAMB = Column(Float)
    IMPORTE = Column(Float)
    IMPORTEME = Column(Float)
    VENDEDOR = Column(String)
    SINCRONIZADO = Column(Boolean, default=False, nullable=False)