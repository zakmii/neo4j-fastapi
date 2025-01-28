from fastapi import APIRouter, HTTPException, Query
from .utils.schema import PredictionResponse, PredictionResult, PredictionRankResponse
from pykeen import predict
import torch
import pandas as pd

router = APIRouter()

# Load a pre-trained PyKEEN model
kge_model = torch.load("app/data/model_epoch_500.pkl")

# Load the mappings for the entities and relations
node_mappings = pd.read_pickle("app/data/HYCDZM_node_id.pkl")

# Load the mappings of C_ID with chemical name
chemical_mappings = pd.read_csv("app/data/ALL_KG_ALL_CHEMICALS.csv")

# Convert chemical mapping to a dictionary for fast lookups
chemical_mapping_dict = dict(zip(chemical_mappings['MY_UNIQ_ID'], chemical_mappings['Chemicals']))

edge_mapping = {'drug_drug' : 0,
                'drug_gene' : 1,
                'gene_drug' : 2,
                'drug_protein' : 3,
                'gene_gene' : 4,
                'gene_metabolite' : 5,
                'gene_phenotype' :6 ,
                'protein_drug' : 7,
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
                'drug_agingphenotype': 20,
                'gene_agingphenotype': 21,
                'gene_hallmark': 22,
                'metabolite_metabolite': 23,
                'gene_epigeneticalterations': 24,
                'gene_genomicinstability': 25,
                'gene_tissue': 26,
                'protein_tissue': 27,
                'protein_agingphenotype': 28,
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
    tags=["KGE Predictions"],
    response_model=PredictionResponse,
    description="Predict the top K tail entities given Gene id, Protein id, Chemical id, Disease name, Phenotype name, AA_Intervention name, Epigenetic_Modification name, Aging_Phenotype name, Hallmark name, Metabolite name, and Tissue name and relation using a PyKEEN KGE model",
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

        # Replace tail names with corresponding Chemicals names using mapping
        #df['Node'] = df['Node'].apply(lambda node: chemical_mapping_dict.get(node, node))

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

@router.get(
    "/get_prediction_rank",
    tags=["KGE Predictions"],
    description="Get the rank and score of a specific tail entity for a given head and relation, along with the maximum score.",
    summary="Retrieve prediction rank and score for a given tail entity",
    response_description="Returns the rank, score, and maximum score of the prediction",
    operation_id="get_prediction_rank",
    response_model=PredictionRankResponse
)
async def get_prediction_rank(
    head: str = Query(..., description="Head entity for the prediction"),
    relation: str = Query(..., description="Relation for the prediction"),
    tail: str = Query(..., description="Tail entity to check for its rank")
):
    """
    Returns the rank, score of the given tail entity, and the maximum score among predictions.
    """
    try:
        # Get IDs for head, relation, and tail
        head_id = get_NodeID(head)
        relation_id = get_EdgeID(relation)
        tail_id = get_NodeID(tail)

        # Perform prediction for all tail entities
        prediction_df = predict.predict_target(
            model=kge_model,
            head=head_id,
            relation=relation_id
        ).df

        # Merge the node names into the DataFrame
        prediction_df = prediction_df.merge(node_mappings, left_on='tail_id', right_on='MappedID', how='left')

        # Find the rank, score of the given tail, and max score
        prediction_df['rank'] = prediction_df['score'].rank(ascending=False, method="dense")
        tail_row = prediction_df[prediction_df['tail_id'] == tail_id]

        if tail_row.empty:
            raise HTTPException(status_code=404, detail=f"Tail entity '{tail}' not found in predictions.")

        tail_rank = int(tail_row['rank'].iloc[0])
        tail_score = float(tail_row['score'].iloc[0])
        max_score = float(prediction_df['score'].max())

        # Return structured response
        return PredictionRankResponse(
            head_entity=head,
            relation=relation,
            tail_entity=tail,
            rank=tail_rank,
            score=tail_score,
            max_score=max_score
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction rank calculation failed: {str(e)}")