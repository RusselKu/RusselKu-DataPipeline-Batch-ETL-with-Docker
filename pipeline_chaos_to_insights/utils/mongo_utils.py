from pymongo import MongoClient

def get_mongo_client():
    """Conexión segura a MongoDB usando las credenciales de tu docker-compose"""
    return MongoClient(
        host="mongodb",
        port=27017,
        username="root",
        password="example",
        authSource="admin"  
    )

def get_raw_collection(db_name, source_name):
    """Obtiene colección raw (creándola si no existe)"""
    client = get_mongo_client()
    return client[db_name][f"raw_{source_name.lower()}"]  

def get_processed_collection(db_name, source_name):
    """Obtiene colección processed (creándola si no existe)"""
    client = get_mongo_client()
    return client[db_name][f"processed_{source_name.lower()}"]  

def get_final_collection(db_name: str, collection_name: str):
    """Obtiene colección final para datos combinados"""
    client = get_mongo_client()
    return client[db_name][f"final_{collection_name.lower()}"]