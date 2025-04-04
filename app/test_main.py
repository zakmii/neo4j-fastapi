from fastapi.testclient import TestClient
from app.main import app  # Import your FastAPI app

client = TestClient(app)  # Create a test client

def test_hello_world():
    response = client.get("/test")  # Simulate a GET request to /test
    assert response.status_code == 200  # Ensure it's successful
    assert response.json() == {"message": "hello world"}  # Validate response
