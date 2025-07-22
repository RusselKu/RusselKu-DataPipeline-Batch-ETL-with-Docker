from pymongo import MongoClient
import streamlit as st

@st.cache_resource(show_spinner=False)
def get_mongo_client():
    """Crea y cachea la conexión MongoDB."""
    try:
        client = MongoClient(
            host="mongodb",  # service de docker-compose
            port=27017,
            username="root",
            password="example",
            authSource="admin"
        )
        client.admin.command("ping")  # Test conection
        return client
    except Exception as e:
        st.error(f"Error conectando a MongoDB: {e}")
        return None

def get_db(db_name="project_db"):
    client = get_mongo_client()
    if client:
        return client[db_name]
    else:
        return None
