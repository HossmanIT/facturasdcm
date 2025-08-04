from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from services.sql_service import SQLService
from services.sync_service import SyncService
from models.schemas import Factura, MondayItem     
from core.database import get_db
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION
)

@app.post("/sync-recent-invoicesdcm")
async def sync_recent_invoices(db: Session = Depends(get_db)):
    """Endpoint para sincronizar facturas recientes con Monday.com y actualizar SQL"""
    try:
        # Obtener facturas recientes
        sql_service = SQLService(db)
        invoices = sql_service.get_recent_invoices()

        # Sincronizar con Monday.com y actualizar SQL
        sync_service = SyncService()
        result = sync_service.sync_invoices(invoices, db)  # Pasamos la sesión de DB

        return {
            "status": "success",
            **result
        }
    except Exception as e:
        db.rollback()  # Asegurar que no quedan transacciones pendientes
        raise HTTPException(status_code=500, detail=str(e))