from pydantic import BaseModel
from typing import Any, Dict, List

class NodeProperties(BaseModel):
    attributes: Dict[str, Any]

class NodeConnection(BaseModel):
    source_node: NodeProperties
    relationship_type: str
    target_node: NodeProperties

class SubgraphResponse(BaseModel):
    connections: List[NodeConnection]
