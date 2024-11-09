from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class Node(BaseModel):
    properties: Dict[str, Any]

class ConnectedNode(BaseModel):
    node_properties: Node
    relationship: str
    connected_node_properties: Node

class SubgraphResponse(BaseModel):
    subgraph: List[ConnectedNode]