#!/bin/bash

set -e

echo "Activating the PyTorch conda environment..."
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate pytorch

REPO_DIR="/home/pushpendrag/ankiss/neo4j-fastapi"
REPO_URL="https://github.com/zakmii/neo4j-fastapi"
BRANCH="generalized_search"

echo "Checking for existing repository at $REPO_DIR..."

if [ -d "$REPO_DIR/.git" ]; then
    echo "Repository exists. Pulling the latest changes..."
    cd "$REPO_DIR"
    git reset --hard
    git checkout $BRANCH
    git pull origin $BRANCH
else
    echo "Repository not found. Cloning from $REPO_URL..."
    cd "$(dirname "$REPO_DIR")"
    GIT_LFS_SKIP_SMUDGE=1 git clone --branch $BRANCH --single-branch $REPO_URL
fi

echo "Copying .env file..."
cp /home/pushpendrag/ankiss/neo4j_env/.env "$REPO_DIR/"

echo "Copying required data files..."
cp /16Tbdrive2/arushis/070225/RotatE/Temp_model/Store_House/node_id_H_KG.pkl "$REPO_DIR/app/data/"
cp /16Tbdrive2/arushis/070225/RotatE/Temp_model/human_checkpoints/model_epoch_99.pkl "$REPO_DIR/app/data/"
cp /16Tbdrive2/arushis/KG_AUGMENTATION/PUSHPA_REFINED_KG_DATA/arushi/MY_REFINED_FILES/ALL_KG_ALL_CHEMICALS_05_02.csv "$REPO_DIR/app/data/"

echo "Killing any existing Gunicorn processes for user $(whoami)..."
# Kill Gunicorn if it was used before, and also kill the python app.main process
pkill -u "$(whoami)" gunicorn || true
pkill -f "python -m app.main" -u "$(whoami)" || true


echo "Starting application server using Poetry..."
cd "$REPO_DIR"
# Run the app/main.py script using poetry, which will use the Uvicorn settings in the file
nohup poetry run gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:1026 > neo4j_api_logs.log 2>&1 &

echo "Deployment completed successfully."
