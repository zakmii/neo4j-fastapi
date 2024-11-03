from fastapi import APIRouter, Depends, HTTPException
from .utils.database import get_neo4j_connection, Neo4jConnection
from .utils.schema import Gene

router = APIRouter()

@router.get("/_get_gene/{gene_id}",description="Get a gene node from the Evo-KG given its ID")
async def _get_gene(gene_id: str, db: Neo4jConnection = Depends(get_neo4j_connection),
                    summary="Get a gene node from the Evo-KG given its ID",
                    response_description="Return the Gene node from the Evo-KG",
                    operation_id="get_gene"):
    query = """
    MATCH (g:Gene)
    WHERE g.id = $id
    RETURN g.id as name;
    """
    result = db.query(query, parameters={"id": gene_id})
    
    if not result:
        raise HTTPException(status_code=404, detail="Gene not found")
    
    return Gene(name=result[0]["name"])

@router.get("/_get_protein/{protein_id}",description="Get a protein node from the Evo-KG given its ID")
async def _get_protein(protein_id: str, db: Neo4jConnection = Depends(get_neo4j_connection),
                       summary="Get a protein node from the Evo-KG given its ID",
                        response_description="Return the Protein node from the Evo-KG",
                       operation_id="get_protein"):
    query = """
    MATCH (p:Protein)
    WHERE p.id = $id
    RETURN p.id as name
    """
    result = db.query(query, parameters={"id": protein_id})
    
    if not result:
        raise HTTPException(status_code=404, detail="Protein not found")
    
    return Gene(name=result[0]["name"])