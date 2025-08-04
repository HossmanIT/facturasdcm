import requests
import json
from typing import Dict, List

class MondayClient:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.api_url = "https://api.monday.com/v2"
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
    
    def execute_query(self, query: str, variables: Dict = None) -> Dict:
        data = {"query": query}
        if variables:
            data["variables"] = variables
        response = requests.post(
            self.api_url,
            json=data,
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error en la API: {response.status_code} - {response.text}")
    
    def get_board_groups(self, board_id: str) -> List[Dict]:
        """
        Obtiene solo los grupos del tablero
        """
        query = """
        query ($board_id: [ID!]) {
            boards(ids: $board_id) {
                groups {
                    id
                    title
                    color
                    position
                }
            }
        }
        """
        variables = {"board_id": [board_id]}
        result = self.execute_query(query, variables)
        boards = result.get("data", {}).get("boards", [])
        if boards:
            return boards[0].get("groups", [])
        return []
    
    def get_board_data_with_groups(self, board_id: str) -> Dict:
        """
        Obtiene datos completos del tablero incluyendo grupos
        """
        # Consulta principal que incluye items con su grupo
        query = """
        query ($board_id: [ID!]) {
            boards(ids: $board_id) {
                id
                name
                description
                state
                columns {
                    id
                    title
                    type
                    settings_str
                }
                groups {
                    id
                    title
                    color
                    position
                }
                items_page(limit: 500) {
                    items {
                        id
                        name
                        state
                        created_at
                        updated_at
                        group {
                            id
                            title
                        }
                        column_values {
                            id
                            type
                            text
                            value
                        }
                    }
                }
            }
        }
        """
        
        variables = {"board_id": [board_id]}
        result = self.execute_query(query, variables)
        
        boards = result.get("data", {}).get("boards", [])
        if not boards:
            return {}
        
        board = boards[0]
        columns = board.get("columns", [])
        groups = board.get("groups", [])
        items = board.get("items_page", {}).get("items", [])
        
        # Crear mapeo de columnas
        column_mapping = {col["id"]: col["title"] for col in columns}
        
        # Crear mapeo de grupos
        group_mapping = {group["id"]: group for group in groups}
        
        # Organizar items por grupo
        groups_with_items = {}
        
        # Inicializar grupos vacíos
        for group in groups:
            groups_with_items[group["id"]] = {
                "group_info": group,
                "items": []
            }
        
        # Procesar items y asignarlos a sus grupos
        for item in items:
            item_group = item.get("group", {})
            group_id = item_group.get("id")
            
            # Formatear item
            formatted_item = {
                "id": item.get("id"),
                "name": item.get("name"),
                "state": item.get("state"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "group_info": item_group,
                "column_data": {}
            }
            
            # Procesar valores de columnas
            for col_value in item.get("column_values", []):
                column_id = col_value.get("id")
                column_title = column_mapping.get(column_id, f"Columna_{column_id}")
                
                formatted_item["column_data"][column_title] = {
                    "column_id": column_id,
                    "type": col_value.get("type"),
                    "text": col_value.get("text"),
                    "raw_value": col_value.get("value")
                }
            
            # Asignar item al grupo correspondiente
            if group_id and group_id in groups_with_items:
                groups_with_items[group_id]["items"].append(formatted_item)
            else:
                # Si no tiene grupo o el grupo no existe, crear grupo "Sin grupo"
                if "sin_grupo" not in groups_with_items:
                    groups_with_items["sin_grupo"] = {
                        "group_info": {"id": "sin_grupo", "title": "Sin Grupo", "color": "#808080"},
                        "items": []
                    }
                groups_with_items["sin_grupo"]["items"].append(formatted_item)
        
        # Convertir a lista ordenada
        formatted_groups = []
        for group_id, group_data in groups_with_items.items():
            if group_data["items"]:  # Solo incluir grupos que tienen items
                formatted_groups.append({
                    "group_id": group_id,
                    "group_title": group_data["group_info"]["title"],
                    "group_color": group_data["group_info"].get("color"),
                    "items_count": len(group_data["items"]),
                    "items": group_data["items"]
                })
        
        return {
            "board_info": {
                "id": board.get("id"),
                "name": board.get("name"),
                "description": board.get("description"),
                "state": board.get("state")
            },
            "columns": columns,
            "column_mapping": column_mapping,
            "groups": formatted_groups,
            "total_items": len(items),
            "total_groups": len(formatted_groups)
        }
    
    def export_to_csv_with_groups(self, board_data: Dict, filename: str = None) -> str:
        """
        Exporta los datos del tablero a CSV incluyendo información de grupos
        """
        if not filename:
            board_name = board_data.get("board_info", {}).get("name", "tablero")
            filename = f"monday_{board_name.replace(' ', '_')}_con_grupos.csv"
        
        import csv
        
        # Recopilar todos los items de todos los grupos
        all_items = []
        for group in board_data.get("groups", []):
            for item in group["items"]:
                item_with_group = item.copy()
                item_with_group["grupo"] = group["group_title"]
                item_with_group["grupo_id"] = group["group_id"]
                all_items.append(item_with_group)
        
        if not all_items:
            print("No hay elementos para exportar")
            return filename
        
        # Obtener todas las columnas únicas
        all_columns = set()
        for item in all_items:
            all_columns.update(item["column_data"].keys())
        
        all_columns = sorted(list(all_columns))
        
        # Escribir CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Grupo', 'ID', 'Nombre', 'Estado', 'Creado', 'Actualizado'] + all_columns
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for item in all_items:
                row = {
                    'Grupo': item.get('grupo', ''),
                    'ID': item['id'],
                    'Nombre': item['name'],
                    'Estado': item['state'],
                    'Creado': item['created_at'],
                    'Actualizado': item['updated_at']
                }
                
                # Agregar datos de columnas
                for col_name in all_columns:
                    col_data = item["column_data"].get(col_name, {})
                    row[col_name] = col_data.get("text", "")
                
                writer.writerow(row)
        
        return filename

def main():
    """
    Función principal para demostrar el uso del script
    """
    # Configuración
    API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUyMjMzNzU5MywiYWFpIjoxMSwidWlkIjo3NDMxODI5OCwiaWFkIjoiMjAyNS0wNi0wNVQwNjowNToxNC4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjMwNjk5OSwicmduIjoidXNlMSJ9.t5ZeM_lS9OhTXymRiYaB0CLjY4AFo60n5dabiSxSpvk"  # Reemplaza con tu token
    BOARD_ID = "9518409013"       # Reemplaza con el ID de tu tablero
    
    try:
        # Inicializar cliente
        client = MondayClient(API_TOKEN)
        
        print(f"=== OBTENIENDO DATOS DEL TABLERO {BOARD_ID} ===")
        
        # Obtener datos completos del tablero con grupos
        board_data = client.get_board_data_with_groups(BOARD_ID)
        
        if board_data:
            # Mostrar información del tablero
            print(f"\nTablero: {board_data['board_info']['name']}")
            print(f"Descripción: {board_data['board_info']['description']}")
            print(f"Total de elementos: {board_data['total_items']}")
            print(f"Total de grupos: {board_data['total_groups']}")
            
            # Mostrar columnas
            print(f"\n=== COLUMNAS ({len(board_data['columns'])}) ===")
            for col in board_data['columns']:
                print(f"- {col['title']} (ID: {col['id']}, Tipo: {col['type']})")
            
            # Mostrar grupos y elementos
            print(f"\n=== GRUPOS Y ELEMENTOS ===")
            for group in board_data['groups']:
                print(f"\n📁 Grupo: {group['group_title']} (ID: {group['group_id']})")
                print(f"   Color: {group.get('group_color', 'N/A')}")
                print(f"   Elementos: {group['items_count']}")
                
                # Mostrar algunos elementos del grupo
                for i, item in enumerate(group['items'][:3]):  # Solo primeros 3
                    print(f"   └─ {item['name']} (ID: {item['id']})")
                    # Mostrar algunos campos con valores
                    for col_name, col_data in list(item['column_data'].items())[:2]:
                        if col_data['text']:
                            print(f"      └─ {col_name}: {col_data['text']}")
                
                if len(group['items']) > 3:
                    print(f"   └─ ... y {len(group['items']) - 3} elementos más")
            
            # Guardar datos en archivo JSON
            json_filename = f"monday_board_{BOARD_ID}_con_grupos.json"
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(board_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Datos JSON guardados en {json_filename}")
            
            # Exportar a CSV con grupos
            csv_filename = client.export_to_csv_with_groups(board_data)
            print(f"✅ Datos CSV con grupos guardados en {csv_filename}")
            
        else:
            print("❌ No se pudieron obtener datos del tablero")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()