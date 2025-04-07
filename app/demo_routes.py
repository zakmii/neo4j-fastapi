from fastapi import FastAPI, APIRouter, HTTPException, Query

router = APIRouter()

@router.get(
    "/hello_world",
    tags=["Demo"],
    description="A simple test endpoint that returns 'Hello, World!'",
    summary="Hello World Test Endpoint",
    response_description="Returns a simple greeting message",
    operation_id="hello_world"
)
async def hello_world():
    return {"message": "Hello, World!"}