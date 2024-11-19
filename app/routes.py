from fastapi import APIRouter, Depends, HTTPException, Query
from .utils.database import get_neo4j_connection, Neo4jConnection
from .utils.schema import NodeProperties, SubgraphResponse, NodeConnection
from typing import List

router = APIRouter()

@router.get(
    "/subgraph",
    description="Retrieve a subgraph of related nodes by specifying the property and value of the start node",
    summary="Get a subgraph of connected nodes based on start node properties",
    response_description="Returns a subgraph of nodes related to the specified node",
    operation_id="get_subgraph",
    response_model=SubgraphResponse
)
async def get_subgraph(
    property_name: str = Query(..., description="Property name of the start node to search for"),
    property_value: str = Query(..., description="Value of the property to search for"),
    db: Neo4jConnection = Depends(get_neo4j_connection)
):
    # Dynamic query to find nodes by the given property
    query = f"""
    MATCH (n {{{property_name}: $property_value}})-[r]-(connected)
    RETURN properties(n) AS node_properties, type(r) AS relationship, properties(connected) AS connected_properties
    LIMIT 30
    """
    
    result = db.query(query, parameters={"property_value": property_value})
    
    if not result:
        raise HTTPException(status_code=404, detail="Node not found or no connections available")
    
    # Construct the subgraph response from the query result
    subgraph = [
        NodeConnection(
            source_node=NodeProperties(attributes=record["node_properties"]),
            relationship_type=record["relationship"],
            target_node=NodeProperties(attributes=record["connected_properties"])
        ) for record in result
    ]
    
    return SubgraphResponse(connections=subgraph)


@router.get(
    "/get_entity",
    response_model=NodeProperties,  # Return the properties of any entity node
    description="Retrieve an entity node from the Evo-KG based on type, property, and value",
    summary="Fetch an entity node based on search criteria",
    response_description="Returns the entity node with specified properties",
    operation_id="get_entity"
)
async def get_entity(
    entity_type: str = Query(..., description="The type of entity (e.g., Gene, Protein, Disease)"),
    property_type: str = Query(..., description="The property to search for (e.g., id, name)"),
    property_value: str = Query(..., description="The value of the property to search for"),
    db: Neo4jConnection = Depends(get_neo4j_connection)
):
    # Query to find the entity by the specified property
    query = f"""
    MATCH (e:{entity_type})
    WHERE e.{property_type} = $property_value
    RETURN e;
    """
    
    result = db.query(query, parameters={"property_value": property_value})
    
    if not result:
        raise HTTPException(status_code=404, detail=f"{entity_type} with {property_type}='{property_value}' not found")
    
    # Return all properties of the node dynamically
    entity_properties = result[0]["e"]
    
    return NodeProperties(attributes=entity_properties)