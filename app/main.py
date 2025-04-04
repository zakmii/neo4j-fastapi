from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import routes, model_routes
from app import test_router

app = FastAPI(
    title="Evo-KG API",
    description="API for interacting with the Evo-KG knowledge graph using Neo4j"
)

# app.include_router(routes.router)
# app.include_router(model_routes.router)
app.include_router(test_router.router)



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
    return {"message": "Welcome to the Evo-KG API. Visit /docs for the API documentation."}