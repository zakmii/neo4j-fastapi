from fastapi import APIRouter, Depends, HTTPException, Query
from .utils.database import get_neo4j_connection, Neo4jConnection
from .utils.schema import NodeProperties, SubgraphResponse, NodeConnection, RelatedEntity, EntityRelationshipsResponse, RelationCheckResponse
from typing import Optional

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
    WHERE LOWER(e.{property_type}) = LOWER($property_value)
    RETURN e;
    """
    
    result = db.query(query, parameters={"property_value": property_value})
    
    if not result:
        raise HTTPException(status_code=404, detail=f"{entity_type} with {property_type}='{property_value}' not found")
    
    # Return all properties of the node dynamically
    entity_properties = result[0]["e"]
    
    return NodeProperties(attributes=entity_properties)

@router.get(
    "/entity_relationships",
    response_model=EntityRelationshipsResponse,
    description="Retrieve the count and list of related entities for a specified entity and optionally by relationship type",
    summary="Fetch related entities by entity and optionally relationship type",
    response_description="Returns the count and details of related entities, optionally filtered by relationship type",
    operation_id="get_entity_relationships"
)
async def get_entity_relationships(
    entity_type: str = Query(..., description="The type of entity to search for (e.g., Gene, Protein)"),
    property_name: str = Query(..., description="The property used to identify the entity (e.g., id, name)"),
    property_value: str = Query(..., description="The value of the property for the entity"),
    relationship_type: Optional[str] = Query(None, description="The type of relationship to filter by (optional)"),
    db: Neo4jConnection = Depends(get_neo4j_connection)
):
    """
    Fetch related entities and optionally filter by relationship type.
    """
    # Build the Cypher query dynamically based on whether relationship_type is provided
    if relationship_type:
        query = f"""
        MATCH (e:{entity_type})-[r:{relationship_type}]-(related)
        WHERE e.{property_name} = $property_value
        RETURN properties(related) AS entity_properties
        LIMIT 30
        """
    else:
        query = f"""
        MATCH (e:{entity_type})--(related)
        WHERE e.{property_name} = $property_value
        RETURN properties(related) AS entity_properties
        LIMIT 30
        """
    
    # Execute the query
    result = db.query(query, parameters={"property_value": property_value})
    
    if not result:
        relationship_message = f" of type '{relationship_type}'" if relationship_type else ""
        raise HTTPException(
            status_code=404,
            detail=f"No relationships{relationship_message} found for {entity_type} with {property_name}='{property_value}'"
        )
    
    # Prepare response data
    related_entities = [
        RelatedEntity(entity_properties=record["entity_properties"])
        for record in result
    ]
    
    return EntityRelationshipsResponse(
        total_relationships=len(related_entities),
        related_entities=related_entities
    )


@router.get(
    "/check_relationship",
    response_model=RelationCheckResponse,
    description="Check if a relationship exists between two entities and return the type of relationship",
    summary="Verify relationship between two entities",
    response_description="Returns whether a relationship exists and its type",
    operation_id="check_relationship"
)
async def check_relationship(
    entity1_type: str = Query(..., description="The type of the first entity (e.g., Gene, Protein)"),
    entity1_property_name: str = Query(..., description="The property name to identify the first entity (e.g., id, name)"),
    entity1_property_value: str = Query(..., description="The property value to identify the first entity"),
    entity2_type: str = Query(..., description="The type of the second entity (e.g., Disease, Protein)"),
    entity2_property_name: str = Query(..., description="The property name to identify the second entity (e.g., id, name)"),
    entity2_property_value: str = Query(..., description="The property value to identify the second entity"),
    db: Neo4jConnection = Depends(get_neo4j_connection)
):
    # Query to check if a relationship exists between the two entities
    query = f"""
    MATCH (e1:{entity1_type})-[r]-(e2:{entity2_type})
    WHERE e1.{entity1_property_name} = $entity1_property_value
      AND e2.{entity2_property_name} = $entity2_property_value
    RETURN type(r) AS relationship_type
    """
    
    result = db.query(query, parameters={
        "entity1_property_value": entity1_property_value,
        "entity2_property_value": entity2_property_value
    })
    
    if not result:
        return RelationCheckResponse(exists=False)
    
    # If a relationship exists, return the type
    return RelationCheckResponse(
        exists=True,
        relationship_type=result[0]["relationship_type"]
    )