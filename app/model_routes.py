from fastapi import APIRouter, HTTPException, Query
from .utils.schema import PredictionResponse, PredictionResult
from pykeen import predict
import torch
import pandas as pd

router = APIRouter()

# Load a pre-trained PyKEEN model
kge_model = torch.load("app/data/model_epoch_500.pkl")

# Load the mappings for the entities and relations
node_mappings = pd.read_pickle("app/data/HYCDZM_node_id.pkl")

edge_mapping = { 'chemical_chemical' : 0,
                'chemical_gene' : 1,
                'gene_chemical' : 2,
                'chemical_protein' : 3,
                'gene_gene' : 4,
                'gene_metabolite' : 5,
                'gene_phenotype' :6 ,
                'protein_chemical' : 7,
                'protein_protein' : 8,
                'phenotype_phenotype': 9,
                'disease_gene': 10,
                'disease_protein': 11,
                'disease_phenotype': 12,
                'disease_drug': 13,
                'drug_disease': 14,
                'disease_disease': 15,
                'gene_disease': 16,
                'gene_protein': 17,
                'protein_disease': 18,
                'protein_gene': 19,
                'chemical_AgingPhenotype': 20,
                'gene_AgingPhenotype': 21,
                'gene_hallmark': 22,
                'metabolite_metabolite': 23,
                'gene-hallmark': 24,
                'gene_gene(genomic instability)': 25,
                'gene_tissue': 26,
                'protein_tissue': 27,
                'protein_AgingPhenotype': 28,
                'intervention_hallmark': 29,
                'hallmark_phenotype': 30
                }

def get_NodeID(node: str) -> int:
    return node_mappings[node_mappings['Node'] == node]['MappedID'].values[0].item()

def get_NodeName(node_id: int) -> str:
    return node_mappings[node_mappings['MappedID'] == node_id]['Node'].values[0].item()

def get_EdgeID(edge: str) -> int:
    return edge_mapping[edge.lower()]

@router.get(
    "/predict_tail",
    tags=["KGE Link Predictions"],
    response_model=PredictionResponse,
    description="Predict the top K tail entities given a head entity and relation using a PyKEEN KGE model",
    summary="Get top-K tail predictions for a given head and relation",
    operation_id="predict_tail"
)
async def predict_tail(
    head: str = Query(..., description="Head entity for the prediction"),
    relation: str = Query(..., description="Relation for the prediction"),
    top_k_predictions: int = Query(10, description="Number of top predictions to return (default is 10)")
):
    """
    Predict the top K tail entities given a head entity and relation.
    """
    try:
        head_id = get_NodeID(head)
        relation_id = get_EdgeID(relation)

        # Perform prediction
        df = predict.predict_target(
            model = kge_model,
            head=head_id,
            relation=relation_id,
        ).df.head(top_k_predictions)

        df = df.merge(node_mappings, left_on='tail_id', right_on='MappedID', how='left')
        df = df[['Node', 'score']]

        # Format the result for the response
        predictions = [
            PredictionResult(tail_entity=tail, score=score) 
            for tail,score in zip(df['Node'],df['score']) 
        ]

        return PredictionResponse(
            head_entity=head,
            relation=relation,
            predictions=predictions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
