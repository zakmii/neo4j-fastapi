from pydantic import BaseModel
from typing import Union, List, Optional

class NodeProperties(BaseModel):
    attributes: dict

class SimilarEntity(BaseModel):
    name: Optional[str] = None
    id: Optional[str] = None

class EntityResponse(BaseModel):
    entity: Union[NodeProperties, List[SimilarEntity]]
    message: Optional[str] = None

class NodeConnection(BaseModel):
    relationship_type: str
    target_node: NodeProperties

class SubgraphResponse(BaseModel):
    source_node: NodeProperties
    connections: List[NodeConnection]

class PredictionResult(BaseModel):
    tail_entity: str
    score: float

class PredictionResponse(BaseModel):
    head_entity: str
    relation: str
    predictions: List[PredictionResult]

class PredictionRankResponse(BaseModel):
    head_entity: str
    relation: str
    tail_entity: str
    rank: int
    score: float
    max_score: float
    
class RelatedEntity(BaseModel):
    entity_properties: dict

class EntityRelationshipsResponse(BaseModel):
    total_relationships: int
    related_entities: List[RelatedEntity]

class RelationCheckResponse(BaseModel):
    exists: bool
    relationship_type: Optional[str] = None