from pymongo import MongoClient
from urllib.parse import quote_plus

def get_mongo_client():
    """Crea una conexión segura a MongoDB usando las credenciales del compose"""
    username = quote_plus("root")  #special characters
    password = quote_plus("example")
    return MongoClient(f"mongodb://{username}:{password}@mongodb:27017/")

def get_raw_collection(db_name: str, source_name: str):
    """Obtiene la colección raw para un source específico"""
    client = get_mongo_client()
    return client[db_name][f"raw_{source_name.lower()}"]

def get_processed_collection(db_name: str, source_name: str):
    """Obtiene la colección processed para un source específico"""
    client = get_mongo_client()
    return client[db_name][f"processed_{source_name.lower()}"]

#functions for apis
def fetch_api_data(url: str, params: dict = None, headers: dict = None):
    """Maneja requests HTTP con manejo de errores básico"""
    import requests
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching API data: {e}")