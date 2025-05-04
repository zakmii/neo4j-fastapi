import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import auth_routes, demo_routes, model_routes, routes
from app.utils.environment import CONFIG

app = FastAPI(
    title="Evo-KG API",
    description="API for interacting with the Evo-KG knowledge graph using Neo4j",
)

app.include_router(routes.router)
app.include_router(auth_routes.router)

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
        "message": "Welcome to the Evo-KG API. Visit /docs for the API documentation.",
    }


if __name__ == "__main__":
    # Ensure this runs from the project root (d:\neo4j-fastapi)
    # Use command: python -m app.main
    # Explanation:
    # `python`: Invokes the Python interpreter.
    # `-m`: Tells Python to load and run a module as a script.
    # `app.main`: Specifies the module to run (looks for `app/__main__.py` or `app/main.py`).
    # This approach ensures that Python adds the project root directory (`d:\neo4j-fastapi`)
    # to the system path, allowing absolute imports within the `app` package (like `from app import routes`)
    # to work correctly, regardless of where the command is run from (as long as `d:\neo4j-fastapi` is accessible).
    # It executes the code within the `if __name__ == "__main__":` block below.
    uvicorn.run(
        "app.main:app",
        host=CONFIG.UVICORN.HOST,
        port=CONFIG.UVICORN.PORT,
        workers=CONFIG.UVICORN.WORKERS,
        reload=CONFIG.UVICORN.RELOAD_ON_CHANGE,
    )
