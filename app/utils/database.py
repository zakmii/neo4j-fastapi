# app/database.py

from neo4j import GraphDatabase
from .environment import Config

class Neo4jConnection:
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

# Dependency injection function for FastAPI routes
def get_neo4j_connection():
    uri = Config.NEO4J_URI
    user = Config.NEO4J_USERNAME
    password = Config.NEO4J_PASSWORD
    return Neo4jConnection(uri, user, password)
