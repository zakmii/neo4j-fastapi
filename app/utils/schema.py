from pydantic import BaseModel

class Gene(BaseModel):
    name: str

class Protein(BaseModel):
    name: str