#!/bin/bash

if [ "$USE_LOCAL_MODEL" == "true" ]; then
    if [ -z "$MODEL_NAME" ] || [ -z "$BASE_URL" ] || [ -z "$API_KEY" ]; then
        echo "Error: MODEL_NAME, BASE_URL, and API_KEY must be set for local model."
        exit 1
    fi
    echo "Configuring deepeval to use a local model..."
    deepeval set-local-model --model-name="$MODEL_NAME" --base-url="$BASE_URL" --api-key="$API_KEY"
else
    echo "Using default OpenAI configuration."
fi

uvicorn app:app --host 0.0.0.0 --port 8000
