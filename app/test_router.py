from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    return {"message": "hello world"}