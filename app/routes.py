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


@router.post(
    "/get_entities",
    response_model=List[NodeProperties],  # Return a list of nodes with their properties
    description="Retrieve multiple entity nodes from the Evo-KG based on their types, properties, and values",
    summary="Fetch multiple entity nodes based on search criteria",
    response_description="Returns the requested entity nodes with specified properties",
    operation_id="get_entities"
)
async def get_entities(
    entities: List[dict] = Query(
        ...,
        description=(
            "A list of dictionaries specifying `entity_type`, `property_type`, and `property_value` "
            "for each entity to retrieve. Example: [{'entity_type': 'Gene', 'property_type': 'id', 'property_value': 'G1'}]"
        )
    ),
    db: Neo4jConnection = Depends(get_neo4j_connection)
):
    """
    Fetch multiple entities based on their types, properties, and values.
    """
    results = []
    for entity in entities:
        entity_type = entity.get("entity_type")
        property_type = entity.get("property_type")
        property_value = entity.get("property_value")

        if not entity_type or not property_type or not property_value:
            raise HTTPException(
                status_code=400,
                detail="Each entity must have `entity_type`, `property_type`, and `property_value` specified."
            )

        # Dynamic query for each entity
        query = f"""
        MATCH (e:{entity_type})
        WHERE e.{property_type} = $property_value
        RETURN e;
        """

        result = db.query(query, parameters={"property_value": property_value})

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"{entity_type} with {property_type}='{property_value}' not found"
            )

        entity_properties = result[0]["e"]
        results.append(NodeProperties(attributes=entity_properties))

    return results

