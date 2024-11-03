from pydantic import BaseModel

class Gene(BaseModel):
    id: str
    description: str

class Protein(BaseModel):
    name: str