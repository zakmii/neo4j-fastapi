from fastapi import FastAPI
from .routes import router

app = FastAPI(
    title="Evo-KG API",
    description="API for interacting with the Evo-KG knowledge graph using Neo4j"
)

app.include_router(router)
