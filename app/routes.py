from fastapi import APIRouter, Depends, HTTPException
from .utils.database import get_neo4j_connection, Neo4jConnection
from .utils.schema import Gene

router = APIRouter()

@router.post("/create_gene/{gene_name}")
async def get_gene(gene_name: str, db: Neo4jConnection = Depends(get_neo4j_connection)):
    query = """
    CREATE (g:Gene {name: $name})
    RETURN g.name as name
    """
    result = db.query(query, parameters={"name": gene_name})
    
    if not result:
        raise HTTPException(status_code=404, detail="Gene not found")
    
    return "gene created"
    #return Gene(name=result[0]["name"], description=result[0]["description"])