import requests
import json
from typing import Dict, Any, Optional
from config.settings import settings
from config.security import verify_credentials
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MondayClient:
    def __init__(self):
        verify_credentials()
        self.headers = {
            "Authorization": settings.MONDAY_API_KEY.get_secret_value(),
            "Content-Type": "application/json"
        }
        self.api_url = settings.MONDAY_API_URL
    
    def get_board_groups(self, board_id: str) -> Dict[str, str]:
        """Obtiene todos los grupos del tablero y retorna un dict {nombre: id}"""
        query = f"""
        query {{
            boards (ids: {board_id}) {{
                groups {{
                    id
                    title
                }}
            }}
        }}
        """
        
        try:
            response = requests.post(
                self.api_url,
                json={'query': query},
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            groups = {}
            if data.get('data', {}).get('boards'):
                for group in data['data']['boards'][0]['groups']:
                    groups[group['title']] = group['id']
            
            return groups
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener grupos: {str(e)}")
            raise
    
    def create_group(self, board_id: str, group_name: str) -> Optional[str]:
        """Crea un nuevo grupo en el tablero y retorna su ID"""
        query = f"""
        mutation {{
            create_group (
                board_id: {board_id},
                group_name: "{group_name}"
            ) {{
                id
            }}
        }}
        """
        
        try:
            response = requests.post(
                self.api_url,
                json={'query': query},
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('data', {}).get('create_group', {}).get('id'):
                return data['data']['create_group']['id']
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al crear grupo: {str(e)}")
            raise
    
    def get_or_create_group_by_date(self, board_id: str, fecha_doc: datetime) -> str:
        """Obtiene o crea el grupo correspondiente al mes de la fecha"""
        # Formatear el nombre del grupo (ej: "ene-2024", "feb-2024")
        meses = {
            1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
            7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"
        }
        
        mes_nombre = meses[fecha_doc.month]
        año = fecha_doc.year
        group_name = f"{mes_nombre}-{año}"
        
        # Obtener grupos existentes
        existing_groups = self.get_board_groups(board_id)
        
        # Si el grupo ya existe, retornar su ID
        if group_name in existing_groups:
            logger.info(f"Grupo '{group_name}' ya existe con ID: {existing_groups[group_name]}")
            return existing_groups[group_name]
        
        # Si no existe, crearlo
        logger.info(f"Creando nuevo grupo: {group_name}")
        group_id = self.create_group(board_id, group_name)
        
        if group_id:
            logger.info(f"Grupo '{group_name}' creado con ID: {group_id}")
            return group_id
        else:
            raise Exception(f"No se pudo crear el grupo {group_name}")
    
    def create_item(self, board_id: str, item_name: str, column_values: Dict[str, Any], group_id: Optional[str] = None):
        """Crea un nuevo ítem en el tablero especificado, opcionalmente en un grupo específico"""
        
        # Si se especifica group_id, incluirlo en la mutación
        group_param = f', group_id: "{group_id}"' if group_id else ''
        
        query = f"""
        mutation {{
            create_item (
                board_id: {board_id},
                item_name: "{item_name}",
                column_values: {json.dumps(json.dumps(column_values))}{group_param}
            ) {{
                id
            }}
        }}
        """
        
        try:
            response = requests.post(
                self.api_url,
                json={'query': query},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al crear ítem en Monday: {str(e)}")
            if e.response is not None:
                logger.error(f"Respuesta del servidor: {e.response.text}")
            raise

# Instancia singleton del cliente
monday_client = MondayClient()