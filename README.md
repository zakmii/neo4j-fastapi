# neo4j-fastapi
API for interacting with the Evo-KG knowledge graph using Neo4j, built with FastAPI.

## Setup and Running

This project uses [Poetry](https://python-poetry.org/) for dependency management.

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/your-username/neo4j-fastapi.git
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
    Create a `.env` file in the project root directory (`d:\neo4j-fastapi`). This file should contain the necessary configuration variables. You can copy the `.env.example` file to `.env` and update the values.

    Example `.env` file (from `.env.example`):
    ```env
#Neo4j settings
NEO4J_URI = neo4j://192.168.24.13:7687
NEO4J_USER = neo4j
NEO4J_PASSWORD = jj7yVSv7Wvo7gxLF0D4XlQoUcesVJ6UNAARsFlK1AIc

#Redis settings
REDIS_HOST = localhost
REDIS_PORT = 6379
REDIS_USERNAME = default
REDIS_PASSWORD = yourpassword
REDIS_DB = 0

#JWT settings
JWT_SECRET_KEY = your_jwt_secret_key
JWT_ALGORITHM = HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

#Optional Uvicorn settings (defaults shown)
UVICORN_HOST = 0.0.0.0
UVICORN_PORT = 1026
UVICORN_WORKERS = 4
UVICORN_RELOAD_ON_CHANGE = True

# Email Configuration (for sending notifications)
MAIL_USERNAME = your_email_username@example.com
MAIL_PASSWORD = your_email_password
MAIL_FROM = sender@example.com
MAIL_PORT = 587
MAIL_SERVER = smtp.example.com
MAIL_FROM_NAME = "Your App Name"
MAIL_STARTTLS = True
MAIL_SSL_TLS = False
MAIL_USE_CREDENTIALS = True
MAIL_VALIDATE_CERTS = True
MAIL_ADMIN_EMAIL = admin@example.com # Email address to receive admin notifications

# Admin Configuration
ADMIN_PASSWORD=your_admin_password_here
    ```

5.  **Run the Application:**
    Use Poetry to run the application module:
    ```bash
    poetry run python -m app.main
    ```
    This command executes `app/main.py` within the Poetry-managed environment, starting the Uvicorn server.

6.  **Access the API:**
    The API will typically be available at `http://127.0.0.1:1026` (or the host/port specified in your environment variables). You can access the interactive documentation at `http://127.0.0.1:1026/docs`.
