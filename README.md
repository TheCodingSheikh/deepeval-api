# Deepeval API

A FastAPI service for evaluating LLM and conversational test cases using the `deepeval` package, designed to minimize conflicts with existing applications.

## Motivation

Integrating the `deepeval` package directly into applications can lead to conflicts due to versioning and dependencies. This service isolates `deepeval` functionality, enabling seamless evaluation without impacting core applications.

## Quick Start

### Option 1: Run with Docker
```bash
docker run -d -p 8000:8000 -e USE_LOCAL_MODEL="true" -e MODEL_NAME="your-model-name" -e BASE_URL="http://your-base-url" -e API_KEY="your-api-key" thecodingsheikh/deepeval-api
```

### Option 2: Deploy with Helm
Refer to the [Helm chart documentation](https://github.com/TheCodingSheikh/helm-charts/tree/main/charts/deepeval-api).

### Environment Variables
- `OPENAI_API_KEY`: OpenAi api key
- `USE_LOCAL_MODEL`: Set to `true` to use a local model instead of openai.
- `MODEL_NAME`, `BASE_URL`, `API_KEY`: Required when `USE_LOCAL_MODEL` is `true`.

## API Endpoints and Examples

### 1. **`/evaluate`**
**Evaluate a single LLM test case.**

**Request**:
```json
{
  "test_case": {
    "input": "What is the capital of France?",
    "actual_output": "The capital of France is Paris."
  },
  "metric_name": "AnswerRelevancyMetric",
  "metric_params": {"threshold": 0.5}
}
```

**Response**:
```json
{
  "score": 0.9,
  "reason": "The response is relevant.",
  "is_successful": true
}
```

### 2. **`/evaluate-conversation`**
**Evaluate a single conversational test case.**

**Request**:
```json
{
  "test_case": {
    "turns": [
      {"input": "Hello", "actual_output": "Hi! How can I help you today?"},
      {"input": "I need to open a new account.", "actual_output": "Of course! Can I get your name, please?"}
    ]
  },
  "metric_name": "KnowledgeRetentionMetric",
  "metric_params": {"threshold": 0.6}
}
```

**Response**:
```json
{
  "score": 0.85,
  "reason": "The conversation maintains context and retains knowledge well.",
  "is_successful": true
}
```

### 3. **`/evaluate-bulk`**
**Evaluate multiple LLM test cases.**

**Request**:
```json
{
  "test_cases": [
    {
      "input": "Why did the chicken cross the road?",
      "actual_output": "To get to the other side."
    },
    {
      "input": "Tell me a joke.",
      "actual_output": "Why did the scarecrow win an award? Because he was outstanding in his field."
    }
  ],
  "metric_names": ["HallucinationMetric"],
  "run_async": true
}
```

**Response**:
```json
{
  "test_case_results": [
    {
      "test_case": 0,
      "score": 0.88,
      "reason": "No hallucinations detected.",
      "is_successful": true
    },
    {
      "test_case": 1,
      "score": 0.95,
      "reason": "Joke is well-formed without hallucinations.",
      "is_successful": true
    }
  ]
}
```

### 4. **`/evaluate-bulk-conversation`**
**Evaluate multiple conversational test cases.**

**Request**:
```json
{
  "test_cases": [
    {
      "turns": [
        {"input": "Hello", "actual_output": "Hi! How can I help you today?"},
        {"input": "Can you tell me the time?", "actual_output": "Sure, it's 2 PM."}
      ]
    }
  ],
  "metric_names": ["ConversationCompletenessMetric"],
  "run_async": true
}
```

**Response**:
```json
{
  "test_case_results": [
    {
      "test_case": 0,
      "score": 0.8,
      "reason": "Conversation covers the necessary details adequately.",
      "is_successful": true
    }
  ]
}
```


## API Schema

### `/evaluate`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "test_case": {
      "input": "string",
      "actual_output": "string",
      "expected_output": "string (optional)",
      "context": ["string (optional)"],
      "retrieval_context": ["string (optional)"],
      "tools_called": ["string (optional)"],
      "expected_tools": ["string (optional)"]
    },
    "metric_name": "string",
    "metric_params": { "key": "value (optional)" }
  }
  ```

### `/evaluate-conversation`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "test_case": {
      "turns": [
        {
          "input": "string",
          "actual_output": "string",
          "expected_output": "string (optional)",
          "context": ["string (optional)"],
          "retrieval_context": ["string (optional)"],
          "tools_called": ["string (optional)"],
          "expected_tools": ["string (optional)"]
        }
      ]
    },
    "metric_name": "string",
    "metric_params": { "key": "value (optional)" }
  }
  ```

### `/evaluate-bulk`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "test_cases": [
      {
        "input": "string",
        "actual_output": "string",
        "expected_output": "string (optional)",
        "context": ["string (optional)"],
        "retrieval_context": ["string (optional)"],
        "tools_called": ["string (optional)"],
        "expected_tools": ["string (optional)"]
      }
    ],
    "metric_names": ["string"],
    "run_async": "boolean (optional)",
    "throttle_value": "integer (optional)",
    "max_concurrent": "integer (optional)",
    "skip_on_missing_params": "boolean (optional)",
    "ignore_errors": "boolean (optional)",
    "verbose_mode": "boolean (optional)",
    "write_cache": "boolean (optional)",
    "use_cache": "boolean (optional)",
    "show_indicator": "boolean (optional)",
    "print_results": "boolean (optional)"
  }
  ```

### `/evaluate-bulk-conversation`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "test_cases": [
      {
        "turns": [
          {
            "input": "string",
            "actual_output": "string",
            "expected_output": "string (optional)",
            "context": ["string (optional)"],
            "retrieval_context": ["string (optional)"],
            "tools_called": ["string (optional)"],
            "expected_tools": ["string (optional)"]
          }
        ]
      }
    ],
    "metric_names": ["string"],
    "run_async": "boolean (optional)",
    "throttle_value": "integer (optional)",
    "max_concurrent": "integer (optional)",
    "skip_on_missing_params": "boolean (optional)",
    "ignore_errors": "boolean (optional)",
    "verbose_mode": "boolean (optional)",
    "write_cache": "boolean (optional)",
    "use_cache": "boolean (optional)",
    "show_indicator": "boolean (optional)",
    "print_results": "boolean (optional)"
  }
  ```
  
## License
Licensed under the MIT License.
