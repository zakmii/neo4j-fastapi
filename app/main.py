from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import routes, model_routes
from app import demo_routes

app = FastAPI(
    title="Evo-KG API",
    description="API for interacting with the Evo-KG knowledge graph using Neo4j",
)

app.include_router(routes.router)

try:
    app.include_router(model_routes.router)
    print("Model routes included successfully")
except Exception as e:
    print(f"Error including model routes: {e}")

# Include demo routes for testing
# Completely for testing purposes
app.include_router(demo_routes.router)

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {
        "message": "Welcome to the Evo-KG API. Visit /docs for the API documentation."
    }
