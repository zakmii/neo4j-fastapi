from fastapi import APIRouter, Depends, HTTPException, Query
from .utils.database import get_neo4j_connection, Neo4jConnection
from .utils.schema import Node, SubgraphResponse, ConnectedNode

router = APIRouter()

@router.get(
    "/subgraph",
    description="Get a subgraph of related nodes by specifying the property and value of the start node",
    summary="Retrieve subgraph based on specified property and value",
    response_description="Returns a subgraph of nodes connected to the specified node",
    operation_id="get_subgraph",
    response_model=SubgraphResponse
)
async def get_subgraph(
    property_name: str = Query(..., description="The property name to search for in the start node"),
    property_value: str = Query(..., description="The value of the property to search for"),
    db: Neo4jConnection = Depends(get_neo4j_connection)
):
    query = f"""
    MATCH (n {{{property_name}: $property_value}})-[r]-(connected)
    RETURN properties(n) AS node_properties, type(r) AS relationship, properties(connected) AS connected_properties
    LIMIT 30
    """
    result = db.query(query, parameters={"property_value": property_value})
    
    if not result:
        raise HTTPException(status_code=404, detail="Node not found or no connections available")
    
    subgraph = [
        ConnectedNode(
            node_properties=Node(properties=record["node_properties"]),
            relationship=record["relationship"],
            connected_node_properties=Node(properties=record["connected_properties"])
        ) for record in result
    ]
    
    return SubgraphResponse(subgraph=subgraph)

@router.get(
    "/get_entity",
    response_model=Node,  # Use a generic model that fits the structure of your entities
    description="Retrieve an entity from the Evo-KG based on entity type, property type, and property value",
    summary="Get an entity from Evo-KG by specified criteria",
    response_description="Returns the requested entity node from the Evo-KG",
    operation_id="get_entity"
)
async def get_entity(
    entity_type: str = Query(..., description="The type of entity to search for, e.g., Gene, Protein, Disease"),
    property_type: str = Query(..., description="The property type to search for, e.g., id, name"),
    property_value: str = Query(..., description="The property value of the entity to search for"),
    db: Neo4jConnection = Depends(get_neo4j_connection)
):
    query = f"""
    MATCH (e:{entity_type})
    WHERE e.{property_type} = $property_value
    RETURN e;
    """
    
    # Execute the query with the dynamic parameters
    result = db.query(query, parameters={"property_value": property_value})
    
    if not result:
        raise HTTPException(status_code=404, detail=f"{entity_type} with {property_type}='{property_value}' not found")
    
    # Retrieve all properties of the node dynamically
    entity_properties = result[0]["e"]
    
    # Return the properties in the response model
    return Node(properties=entity_properties)
