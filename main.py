from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from deepeval.test_case import LLMTestCase, ConversationalTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    HallucinationMetric,
    SummarizationMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    RagasMetric,
    ToxicityMetric,
    BiasMetric,
    GEval,
    KnowledgeRetentionMetric,
    ConversationCompletenessMetric,
    ConversationRelevancyMetric
)
import os

app = FastAPI()

METRIC_CLASSES = {
    "AnswerRelevancy": AnswerRelevancyMetric,
    "Hallucination": HallucinationMetric,
    "Summarization": SummarizationMetric,
    "Faithfulness": FaithfulnessMetric,
    "ContextualRelevancy": ContextualRelevancyMetric,
    "ContextualPrecision": ContextualPrecisionMetric,
    "ContextualRecall": ContextualRecallMetric,
    "Ragas": RagasMetric,
    "Toxicity": ToxicityMetric,
    "Bias": BiasMetric,
    "GEval": GEval
}

CONVERSATIONAL_METRIC_CLASSES = {
    "KnowledgeRetention": KnowledgeRetentionMetric,
    "ConversationCompleteness": ConversationCompletenessMetric,
    "ConversationRelevancy": ConversationRelevancyMetric
}

class LLMTestCaseRequest(BaseModel):
    input: str
    actual_output: str
    expected_output: Optional[str] = None
    context: Optional[List[str]] = None
    retrieval_context: Optional[List[str]] = None
    tools_called: Optional[List[str]] = None
    expected_tools: Optional[List[str]] = None

class SingleEvaluationRequest(BaseModel):
    test_case: LLMTestCaseRequest
    metric_name: str  # Name of the metric to use
    metric_params: Optional[Dict[str, Union[str, int, float]]] = None

class ConversationalTestCaseRequest(BaseModel):
    turns: List[LLMTestCaseRequest]

class SingleConversationalEvaluationRequest(BaseModel):
    test_case: ConversationalTestCaseRequest
    metric_name: str
    metric_params: Optional[Dict[str, Union[str, int, float]]] = None 

class MetricResponse(BaseModel):
    score: float
    reason: str
    is_successful: bool

class BulkEvaluationRequest(BaseModel):
    test_cases: List[LLMTestCaseRequest]  
    metric_names: List[str] 
    hyperparameters: Optional[Dict[str, Union[str, int, float]]] = None
    run_async: Optional[bool] = True
    throttle_value: Optional[int] = 0
    max_concurrent: Optional[int] = 100
    skip_on_missing_params: Optional[bool] = False
    ignore_errors: Optional[bool] = False
    verbose_mode: Optional[bool] = None
    write_cache: Optional[bool] = True
    use_cache: Optional[bool] = False
    show_indicator: Optional[bool] = True
    print_results: Optional[bool] = True

class BulkConversationalEvaluationRequest(BaseModel):
    test_cases: List[ConversationalTestCaseRequest]
    metric_names: List[str]
    hyperparameters: Optional[Dict[str, Union[str, int, float]]] = None
    run_async: Optional[bool] = True
    throttle_value: Optional[int] = 0
    max_concurrent: Optional[int] = 100
    skip_on_missing_params: Optional[bool] = False
    ignore_errors: Optional[bool] = False
    verbose_mode: Optional[bool] = None
    write_cache: Optional[bool] = True
    use_cache: Optional[bool] = False
    show_indicator: Optional[bool] = True
    print_results: Optional[bool] = True

class BulkEvaluationResponse(BaseModel):
    test_case_results: List[Dict[str, Union[str, float, bool]]]

@app.post("/evaluate", response_model=MetricResponse)
async def evaluate_test_case(request_data: SingleEvaluationRequest):
    try:
        test_case = LLMTestCase(
            input=request_data.test_case.input,
            actual_output=request_data.test_case.actual_output,
            expected_output=request_data.test_case.expected_output,
            context=request_data.test_case.context or [],
            retrieval_context=request_data.test_case.retrieval_context or [],
            tools_called=request_data.test_case.tools_called or [],
            expected_tools=request_data.test_case.expected_tools or []
        )
        
        if not request_data.metric_name or request_data.metric_name not in METRIC_CLASSES:
            raise HTTPException(status_code=400, detail="Metric not supported or not provided")
        
        metric_class = METRIC_CLASSES[request_data.metric_name]
        metric = metric_class(**(request_data.metric_params or {}))
        
        metric.measure(test_case)
        
        response = MetricResponse(
            score=metric.score,
            reason=metric.reason,
            is_successful=metric.is_successful()
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in processing: {str(e)}")

@app.post("/evaluate-conversation", response_model=MetricResponse)
async def evaluate_conversational_test_case(request_data: SingleConversationalEvaluationRequest):
    try:
        turns = [
            LLMTestCase(
                input=turn.input,
                actual_output=turn.actual_output,
                expected_output=turn.expected_output,
                context=turn.context or [],
                retrieval_context=turn.retrieval_context or [],
                tools_called=turn.tools_called or [],
                expected_tools=turn.expected_tools or []
            )
            for turn in request_data.test_case.turns
        ]

        test_case = ConversationalTestCase(turns=turns)

        if not request_data.metric_name or request_data.metric_name not in CONVERSATIONAL_METRIC_CLASSES:
            raise HTTPException(status_code=400, detail="Metric not supported or not provided")

        metric_class = CONVERSATIONAL_METRIC_CLASSES[request_data.metric_name]
        metric = metric_class(**(request_data.metric_params or {}))

        metric.measure(test_case)

        response = MetricResponse(
            score=metric.score,
            reason=metric.reason,
            is_successful=metric.is_successful()
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in processing: {str(e)}")

@app.post("/evaluate-bulk", response_model=BulkEvaluationResponse)
async def evaluate_bulk(request_data: BulkEvaluationRequest):
    try:
        test_cases = [
            LLMTestCase(
                input=case.input,
                actual_output=case.actual_output,
                expected_output=case.expected_output,
                context=case.context or [],
                retrieval_context=case.retrieval_context or [],
                tools_called=case.tools_called or [],
                expected_tools=case.expected_tools or []
            )
            for case in request_data.test_cases
        ]

        metrics = []
        for metric_name in request_data.metric_names:
            if metric_name not in METRIC_CLASSES:
                raise HTTPException(status_code=400, detail=f"Metric '{metric_name}' not supported")
            metrics.append(METRIC_CLASSES[metric_name]())

        results = evaluate(
            test_cases=test_cases,
            metrics=metrics,
            hyperparameters=request_data.hyperparameters,
            run_async=request_data.run_async,
            throttle_value=request_data.throttle_value,
            max_concurrent=request_data.max_concurrent,
            skip_on_missing_params=request_data.skip_on_missing_params,
            ignore_errors=request_data.ignore_errors,
            verbose_mode=request_data.verbose_mode,
            write_cache=request_data.write_cache,
            use_cache=request_data.use_cache,
            show_indicator=request_data.show_indicator,
            print_results=request_data.print_results
        )

        response_data = [
            {
                "test_case": idx,
                "score": result.score,
                "reason": result.reason,
                "is_successful": result.is_successful()
            }
            for idx, result in enumerate(results)
        ]

        return BulkEvaluationResponse(test_case_results=response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in processing: {str(e)}")

@app.post("/evaluate-bulk-conversation", response_model=BulkEvaluationResponse)
async def evaluate_bulk_conversational(request_data: BulkConversationalEvaluationRequest):
    try:
        test_cases = [
            ConversationalTestCase(
                turns=[
                    LLMTestCase(
                        input=turn.input,
                        actual_output=turn.actual_output,
                        expected_output=turn.expected_output,
                        context=turn.context or [],
                        retrieval_context=turn.retrieval_context or [],
                        tools_called=turn.tools_called or [],
                        expected_tools=turn.expected_tools or []
                    )
                    for turn in conv_case.turns
                ]
            )
            for conv_case in request_data.test_cases
        ]

        metrics = []
        for metric_name in request_data.metric_names:
            if metric_name not in CONVERSATIONAL_METRIC_CLASSES:
                raise HTTPException(status_code=400, detail=f"Metric '{metric_name}' not supported")
            metrics.append(CONVERSATIONAL_METRIC_CLASSES[metric_name]())

        results = evaluate(
            test_cases=test_cases,
            metrics=metrics,
            hyperparameters=request_data.hyperparameters,
            run_async=request_data.run_async,
            throttle_value=request_data.throttle_value,
            max_concurrent=request_data.max_concurrent,
            skip_on_missing_params=request_data.skip_on_missing_params,
            ignore_errors=request_data.ignore_errors,
            verbose_mode=request_data.verbose_mode,
            write_cache=request_data.write_cache,
            use_cache=request_data.use_cache,
            show_indicator=request_data.show_indicator,
            print_results=request_data.print_results
        )

        response_data = [
            {
                "test_case": idx,
                "score": result.score,
                "reason": result.reason,
                "is_successful": result.is_successful()
            }
            for idx, result in enumerate(results)
        ]

        return BulkEvaluationResponse(test_case_results=response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in processing: {str(e)}")
