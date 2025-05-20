import pandas as pd
import torch
from fastapi import APIRouter, HTTPException, Query
from pykeen import predict

from app.utils.schema import (
    PredictionRankResponse,
    PredictionResponse,
    PredictionResult,
)

router = APIRouter()

# Define the path for data loading
model_path = "app/data/model_epoch_94.pkl"
node_mappings_path = "app/data/node_id_H_KG.pkl"

# Attempt to load the pre-trained PyKEEN model
try:
    # Load the model onto the appropriate device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    kge_model = torch.load(model_path, map_location=device, weights_only=False)

except FileNotFoundError:
    raise FileNotFoundError(
        f"KGE model file not found. Please ensure '{model_path}' exists.",
    )
except Exception as e:
    raise RuntimeError(f"Error loading KGE model: {e!s}")

# Load the mappings for the entities and relations
try:
    node_mappings = pd.read_pickle(node_mappings_path)
except FileNotFoundError:
    raise Exception(
        f"Node mappings file not found. Please ensure {node_mappings_path} exists in the app/data directory.",
    )
except Exception as e:
    raise Exception(f"Error loading node mappings: {e!s}")

###Now we fetch info from the database after every prediction which gets more information###

# Load the mappings of C_ID with chemical name
# try:
#     chemical_mappings = pd.read_csv("app/data/ALL_KG_ALL_CHEMICALS_05_02.csv")
# except FileNotFoundError:
#     raise Exception(
#         "Chemical mappings file not found. Please ensure ALL_KG_ALL_CHEMICALS_05_02.csv exists in the app/data directory.",
#     )
# except Exception as e:
#     raise Exception(f"Error loading chemical mappings: {e!s}")

# # Convert chemical mapping to a dictionary for fast lookups
# chemical_mapping_dict = dict(
#     zip(chemical_mappings["MY_UNIQ_ID"], chemical_mappings["Chemicals"]),
# )


edge_mapping = {
    "phenotype_chemicalentity": 0,
    "chemicalentity_phenotype": 0,
    "mutation_disease": 1,  # reverse relation exists with different ID (40)
    "molecularfunction_chemicalentity": 2,
    "chemicalentity_molecularfunction": 2,
    "disease_anatomy": 3,
    "anatomy_disease": 3,
    "chemicalentity_disease": 4,  # reverse relation exists with different ID (39)
    "disease_disease": 5,
    "biologicalprocess_gene": 6,  # reverse relation exists with different ID (46)
    "protein_protein": 7,
    "gene_phenotype": 8,  # reverse relation exists with different ID (25)
    "protein_disease": 9,
    "disease_protein": 9,
    "anatomy_gene": 10,  # reverse relation exists with different ID (36)
    "chemicalentity_biologicalprocess": 11,  # reverse relation exists with different ID (57)
    "disease_gene": 12,  # reverse relation exists with different ID (16)
    "gene_cellularcomponent": 13,  # reverse relation exists with different ID (15)
    "chemicalentity_chemicalentity": 14,
    "cellularcomponent_gene": 15,
    "gene_disease": 16,
    "protein_cellularcomponent": 17,
    "cellularcomponent_protein": 17,
    "protein_phenotype": 18,
    "phenotype_protein": 18,
    "mutation_protein": 19,
    "protein_mutation": 19,
    "chemicalentity_gene": 20,  # reverse relation exists with different ID (41)
    "chemicalentity_tissue": 21,
    "tissue_chemicalentity": 21,
    "chemicalentity_protein": 22,
    "protein_chemicalentity": 22,
    "biologicalprocess_biologicalprocess": 23,
    "phenotype_phenotype": 24,
    "phenotype_gene": 25,
    "chemicalentity_inhibits_biologicalprocess": 26,
    "biologicalprocess_inhibits_chemicalentity": 26,  # Assuming "inhibits" stays in middle
    "gene_inhibits_biologicalprocess": 27,
    "biologicalprocess_inhibits_gene": 27,  # Assuming "inhibits" stays in middle
    "protein_biologicalprocess": 28,
    "biologicalprocess_protein": 28,
    "gene_promotes_biologicalprocess": 29,
    "biologicalprocess_promotes_gene": 29,  # Assuming "promotes" stays in middle
    "gene_molecularfunction": 30,
    "molecularfunction_gene": 30,
    "gene_pathway": 31,  # reverse relation exists with different ID (38)
    "chemicalentity_pathway": 32,
    "pathway_chemicalentity": 32,
    "gene_tissue": 33,
    "tissue_gene": 33,
    "disease_phenotype": 34,  # reverse relation exists with different ID (37)
    "chemicalentity_mutation": 35,
    "mutation_chemicalentity": 35,
    "gene_anatomy": 36,
    "phenotype_disease": 37,
    "pathway_gene": 38,
    "disease_chemicalentity": 39,
    "disease_mutation": 40,
    "gene_chemicalentity": 41,
    "protein_pathway": 42,
    "pathway_protein": 42,
    "gene_protein": 43,
    "protein_gene": 43,
    "gene_noeffect_biologicalprocess": 44,
    "biologicalprocess_noeffect_gene": 44,  # Assuming "noeffect" stays in middle
    "chemicalentity_promotes_biologicalprocess": 45,
    "biologicalprocess_promotes_chemicalentity": 45,  # Assuming "promotes" stays in middle
    "gene_biologicalprocess": 46,
    "protein_molecularfunction": 47,
    "molecularfunction_protein": 47,
    "mutation_gene": 48,  # reverse relation exists with different ID (51)
    "gene_gene": 49,
    "molecularfunction_molecularfunction": 50,
    "gene_mutation": 51,
    "molecularfunction_biologicalprocess": 52,
    "biologicalprocess_molecularfunction": 52,
    "protein_tissue": 53,
    "tissue_protein": 53,
    "cellularcomponent_cellularcomponent": 54,
    "pathway_pathway": 55,
    "anatomy_anatomy": 56,
    "biologicalprocess_chemicalentity": 57,
    "plantextract_chemicalentity": 58,
    "chemicalentity_plantextract": 58,
    "plantextract_disease": 59,
    "disease_plantextract": 59,
    "pmid_cellularcomponent": 60,
    "cellularcomponent_pmid": 60,
    "pmid_chemicalentity": 61,
    "chemicalentity_pmid": 61,
    "pmid_disease": 62,
    "disease_pmid": 62,
    "pmid_protein": 63,
    "protein_pmid": 63,
    "pmid_tissue": 64,
    "tissue_pmid": 64,
    "species_associatedwith_nodes": 65,
    "nodes_associatedwith_species": 65,  # Assuming "associatedwith" stays in middle
}

# def get_NodeID(node: str) -> int:
#     return node_mappings[node_mappings['Node'] == node]['MappedID'].values[0].item()


# def get_NodeName(node_id: int) -> str:
#     return node_mappings[node_mappings["MappedID"] == node_id]["Node"].values[0].item()


def get_EdgeID(edge: str) -> int:
    return edge_mapping[edge.lower()]


@router.get(
    "/predict_tail",
    tags=["KGE Predictions"],
    response_model=PredictionResponse,
    description="Predict the top K tail entities given 'model_id' of entities and relation using a PyKEEN KGE model",
    summary="Get top-K tail predictions for a given head and relation",
    operation_id="predict_tail",
)
async def predict_tail(
    head: str = Query(
        ...,
        description="model_id for the head entity for the prediction",
    ),
    relation: str = Query(..., description="Relation for the prediction"),
    top_k_predictions: int = Query(
        10,
        description="Number of top predictions to return (default is 10)",
    ),
):
    """Predict the top K tail entities given a head entity and relation."""
    try:
        head_id = int(head)
        relation_id = get_EdgeID(relation)

        # Perform prediction
        df = predict.predict_target(
            model=kge_model,
            head=head_id,
            relation=relation_id,
        ).df.head(top_k_predictions)

        df = df.merge(node_mappings, left_on="tail_id", right_on="MappedID", how="left")
        df = df[["Node", "score"]]

        ###Now we fetch info from the database after every prediction which gets more information###

        # Replace tail names with corresponding Chemicals names using mapping
        # df["Node"] = df["Node"].apply(
        #     lambda node: chemical_mapping_dict.get(node, node),
        # )

        # Format the result for the response
        predictions = [
            PredictionResult(tail_entity=tail, score=score)
            for tail, score in zip(df["Node"], df["score"])
        ]

        return PredictionResponse(
            head_entity=head,
            relation=relation,
            predictions=predictions,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e!s}")


@router.get(
    "/get_prediction_rank",
    tags=["KGE Predictions"],
    description="Get the rank and score of a specific tail entity for a given head and relation, along with the maximum score.",
    summary="Retrieve prediction rank and score for a given tail entity",
    response_description="Returns the rank, score, and maximum score of the prediction",
    operation_id="get_prediction_rank",
    response_model=PredictionRankResponse,
)
async def get_prediction_rank(
    head: str = Query(..., description="model_id for head entity for the prediction"),
    relation: str = Query(..., description="Relation for the prediction"),
    tail: str = Query(
        ...,
        description="model_id for tail entity to check for its rank",
    ),
):
    """Returns the rank, score of the given tail entity, and the maximum score among predictions."""
    try:
        # Get IDs for head, relation, and tail
        head_id = int(head)
        relation_id = get_EdgeID(relation)
        tail_id = int(tail)

        # Perform prediction for all tail entities
        prediction_df = predict.predict_target(
            model=kge_model,
            head=head_id,
            relation=relation_id,
        ).df

        # Merge the node names into the DataFrame
        prediction_df = prediction_df.merge(
            node_mappings,
            left_on="tail_id",
            right_on="MappedID",
            how="left",
        )

        # Find the rank, score of the given tail, and max score
        prediction_df["rank"] = prediction_df["score"].rank(
            ascending=False,
            method="dense",
        )
        tail_row = prediction_df[prediction_df["tail_id"] == tail_id]

        if tail_row.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Tail entity '{tail}' not found in predictions.",
            )

        tail_rank = int(tail_row["rank"].iloc[0])
        tail_score = float(tail_row["score"].iloc[0])
        max_score = float(prediction_df["score"].max())

        # Return structured response
        return PredictionRankResponse(
            head_entity=head,
            relation=relation,
            tail_entity=tail,
            rank=tail_rank,
            score=tail_score,
            max_score=max_score,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction rank calculation failed: {e!s}",
        )
