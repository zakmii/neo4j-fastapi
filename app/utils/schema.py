from pydantic import BaseModel
from typing import Any, Dict, List

class NodePropertiesQuery(BaseModel):
    entity_type: str  # The type of the entity (e.g., Gene, Disease, Protein)
    property_type: str  # The property to search by (e.g., id, name)
    property_value: str  # The value of the property to match

class NodeProperties(BaseModel):
    attributes: Dict[str, Any]

class NodeConnection(BaseModel):
    source_node: NodeProperties
    relationship_type: str
    target_node: NodeProperties

class SubgraphResponse(BaseModel):
    connections: List[NodeConnection]
