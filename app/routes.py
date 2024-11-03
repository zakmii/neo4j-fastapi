from fastapi import APIRouter, Depends, HTTPException, Query
from .utils.database import get_neo4j_connection, Neo4jConnection
from .utils.schema import Gene, Protein

router = APIRouter()

@router.get("/_get_gene",
            response_model= Gene,
            description="Get a gene node from the Evo-KG given its ID",
            summary="Get a gene node from the Evo-KG given its ID",
            response_description="Return the Gene node from the Evo-KG",
            operation_id="get_gene")
async def get_gene(gene_id: str = Query(...,description="The gene id to search for"),
                   db: Neo4jConnection = Depends(get_neo4j_connection)):
    query = """
    MATCH (g:Gene)
    WHERE g.id = $id
    RETURN g;
    """
    result = db.query(query, parameters={"id": gene_id})
    
    if not result:
        raise HTTPException(status_code=404, detail="Gene not found")
    
    return Gene(id=result[0]["g"]["id"], description=result[0]["g"]["description"])

@router.get("/_get_protein",
            response_model= Protein,
            description="Get a protein node from the Evo-KG given its ID",
            summary="Get a protein node from the Evo-KG given its ID",
            response_description="Return the Protein node from the Evo-KG",
            operation_id="get_protein")
async def get_protein(protein_id: str = Query(...,description="The protein id to search for"), 
                      db: Neo4jConnection = Depends(get_neo4j_connection)):
    query = """
    MATCH (p:Protein)
    WHERE p.id = $id
    RETURN p.id as name
    """
    result = db.query(query, parameters={"id": protein_id})
    
    if not result:
        raise HTTPException(status_code=404, detail="Protein not found")
    
    return Protein(name=result[0]["name"])