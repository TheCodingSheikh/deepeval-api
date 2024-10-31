#!/bin/bash

deepeval set-local-model --model-name="$MODEL_NAME" --base-url="$BASE_URL" --api-key="$API_KEY"

uvicorn app:app --host 0.0.0.0 --port 8000
