# neo4j-fastapi

API for interacting with the Evo-KG knowledge graph using Neo4j, built with FastAPI.

## Setup and Running

This project uses [Poetry](https://python-poetry.org/) for dependency management.

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd neo4j-fastapi
    ```

2.  **Install Poetry:**
    Follow the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).

3.  **Install Dependencies:**
    Navigate to the project root directory (`d:\neo4j-fastapi`) and run:
    ```bash
    poetry install
    ```
    This will create a virtual environment and install all necessary packages specified in `pyproject.toml`.

4.  **Set Up Environment Variables:**
    Create a `.env` file in the project root directory (`d:\neo4j-fastapi`). This file should contain the necessary configuration variables. Refer to `app/utils/environment.py` for the required variables (e.g., `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `REDIS_HOST`, `REDIS_PORT`, `JWT_SECRET_KEY`).

    Example `.env` file:
    ```env
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USERNAME=neo4j
    NEO4J_PASSWORD=your_neo4j_password

    REDIS_HOST=localhost
    REDIS_PORT=6379
    REDIS_USERNAME=your_redis_username
    REDIS_PASSWORD=your_redis_password
    REDIS_DB=0

    # IMPORTANT: Change this to a strong, unique secret key!
    JWT_SECRET_KEY=your_very_strong_secret_key_here
    JWT_ALGORITHM=HS256
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

5.  **Run the Application:**
    Use Poetry to run the application module:
    ```bash
    poetry run python -m app.main
    ```
    This command executes `app/main.py` within the Poetry-managed environment, starting the Uvicorn server.

6.  **Access the API:**
    The API will typically be available at `http://127.0.0.1:1026` (or the host/port specified in your environment variables). You can access the interactive documentation at `http://127.0.0.1:1026/docs`.
