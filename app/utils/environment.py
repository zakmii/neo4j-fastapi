# Packages and functions for loading environment variables
import os
from dotenv import load_dotenv, find_dotenv

# Load environment from disk first, then apply any defaults
load_dotenv(find_dotenv('.env'))

class Config:
    # Neo4j driver execution
    NEO4J_URI = os.environ.get('NEO4J_URI','')
    NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME', 'neo4j')
    NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD','')