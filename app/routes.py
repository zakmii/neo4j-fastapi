from fastapi import APIRouter, Depends, HTTPException, Query, Body
from .utils.database import get_neo4j_connection, Neo4jConnection
from .utils.schema import NodePropertiesQuery, NodeProperties, SubgraphResponse, NodeConnection
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


@router.post(
    "/get_entity",
    response_model=List[NodeProperties],  # List of entity responses
    description="Retrieve information for multiple entities from the Evo-KG",
    summary="Fetch multiple entities based on search criteria",
    response_description="Returns the requested entities with their properties",
    operation_id="get_entity"
)
async def get_entity(
    entities: List[NodePropertiesQuery] = Body(..., description="List of entity queries"),
    db: Neo4jConnection = Depends(get_neo4j_connection)
):
    results = []

    for query in entities:
        neo4j_query = f"""
        MATCH (e:{query.entity_type})
        WHERE e.{query.property_type} = $property_value
        RETURN e;
        """
        query_result = db.query(neo4j_query, parameters={"property_value": query.property_value})
        
        if not query_result:
            raise HTTPException(status_code=404, detail=f"{query.entity_type} with {query.property_type}='{query.property_value}' not found")
        
        results.append(NodeProperties(attributes=query_result[0]["e"]))

    return results