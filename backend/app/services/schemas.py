"""
Pydantic Schemas for ML Operations
Defines data models for experiments, batch jobs, and ML configurations
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime
from enum import Enum


class ExperimentStatus(str, Enum):
    """Status of ML experiment"""
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchJobStatus(str, Enum):
    """Status of batch job"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProblemType(str, Enum):
    """Type of ML problem"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    RECOMMENDATION = "recommendation"


class ModelType(str, Enum):
    """Type of ML model"""
    RANDOM_FOREST = "random_forest"
    LINEAR_REGRESSION = "linear_regression"
    LOGISTIC_REGRESSION = "logistic_regression"
    XGBOOST = "xgboost"
    NEURAL_NETWORK = "neural_network"
    LSTM = "lstm"
    TRANSFORMER = "transformer"
    ISOLATION_FOREST = "isolation_forest"
    KMEANS = "kmeans"


# ==================== Experiment Schemas ====================

class AlgorithmConfig(BaseModel):
    """Configuration for a single algorithm"""
    name: str = Field(..., description="Algorithm name")
    model_type: ModelType = Field(..., description="Type of model")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model hyperparameters")
    priority: int = Field(default=1, description="Priority for execution (1=highest)")
    rationale: Optional[str] = Field(None, description="Why this algorithm was chosen")


class FeatureConfig(BaseModel):
    """Feature engineering configuration"""
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="Feature description")
    transformation: str = Field(..., description="Transformation method")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Transformation parameters")


class EvaluationMetric(BaseModel):
    """Evaluation metric configuration"""
    name: str = Field(..., description="Metric name (e.g., 'accuracy', 'rmse')")
    weight: float = Field(default=1.0, description="Weight in overall evaluation")
    threshold: Optional[float] = Field(None, description="Success threshold")
    higher_is_better: bool = Field(default=True, description="Whether higher values are better")


class ExperimentPlan(BaseModel):
    """ML Experiment Plan Schema"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    experiment_id: str = Field(..., description="Unique experiment identifier")
    name: str = Field(..., description="Human-readable experiment name")
    description: str = Field(..., description="Detailed description of the experiment")
    
    # Problem definition
    problem_type: ProblemType = Field(..., description="Type of ML problem")
    target_variable: Optional[str] = Field(None, description="Target variable name")
    objective: str = Field(..., description="Business objective")
    
    # Data configuration
    data_sources: List[str] = Field(..., description="List of data sources")
    feature_columns: List[str] = Field(default_factory=list, description="Input feature columns")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range for training data")
    
    # Model configuration
    algorithms: List[AlgorithmConfig] = Field(..., description="Algorithms to test")
    feature_engineering: List[FeatureConfig] = Field(default_factory=list, description="Feature engineering steps")
    preprocessing_steps: List[str] = Field(default_factory=list, description="Data preprocessing steps")
    
    # Evaluation configuration
    evaluation_metrics: List[EvaluationMetric] = Field(..., description="Evaluation metrics")
    validation_strategy: str = Field(default="time_series_split", description="Validation strategy")
    test_size: float = Field(default=0.2, description="Test set size ratio")
    
    # Resource constraints
    max_training_time_hours: Optional[int] = Field(None, description="Maximum training time")
    max_memory_gb: Optional[int] = Field(None, description="Maximum memory usage")
    compute_requirements: Optional[str] = Field(None, description="Compute requirements (cpu/gpu)")
    
    # Success criteria
    success_criteria: List[str] = Field(..., description="Definition of experiment success")
    minimum_performance: Dict[str, float] = Field(default_factory=dict, description="Minimum performance thresholds")
    
    # Timeline and metadata
    estimated_duration_hours: Optional[int] = Field(None, description="Estimated completion time")
    priority: int = Field(default=1, description="Experiment priority")
    tags: List[str] = Field(default_factory=list, description="Experiment tags")
    
    # Planning metadata
    planned_by: Optional[str] = Field(None, description="Who planned the experiment")
    planned_at: datetime = Field(default_factory=datetime.utcnow, description="When experiment was planned")
    auto_generated: bool = Field(default=False, description="Whether plan was auto-generated")


class ExperimentResult(BaseModel):
    """Results of an ML experiment"""
    experiment_id: str = Field(..., description="Experiment identifier")
    status: ExperimentStatus = Field(..., description="Experiment status")
    
    # Performance metrics
    metrics: Dict[str, float] = Field(default_factory=dict, description="Evaluation metrics")
    best_model: Optional[str] = Field(None, description="Best performing model")
    model_performance: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Performance by model")
    
    # Training details
    training_duration_seconds: Optional[float] = Field(None, description="Training time")
    total_samples: Optional[int] = Field(None, description="Total training samples")
    feature_importance: Optional[Dict[str, float]] = Field(None, description="Feature importance scores")
    
    # Model artifacts
    model_path: Optional[str] = Field(None, description="Path to saved model")
    artifacts: Dict[str, str] = Field(default_factory=dict, description="Paths to other artifacts")
    
    # Execution metadata
    started_at: Optional[datetime] = Field(None, description="When execution started")
    completed_at: Optional[datetime] = Field(None, description="When execution completed")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    logs: List[str] = Field(default_factory=list, description="Execution logs")


# ==================== Batch Job Schemas ====================

class BatchJobRequest(BaseModel):
    """Request for batch processing job"""
    job_id: str = Field(..., description="Unique job identifier")
    job_type: str = Field(..., description="Type of batch job")
    description: str = Field(..., description="Job description")
    
    # Input data
    input_data: List[Dict[str, Any]] = Field(..., description="Input data items")
    input_source: Optional[str] = Field(None, description="Source of input data")
    
    # Processing configuration
    batch_size: int = Field(default=100, description="Processing batch size")
    parallel_workers: int = Field(default=1, description="Number of parallel workers")
    timeout_seconds: Optional[int] = Field(None, description="Job timeout")
    
    # Parameters
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Job parameters")
    context: Optional[str] = Field(None, description="Additional context")
    
    # Metadata
    created_by: Optional[str] = Field(None, description="Job creator")
    priority: int = Field(default=1, description="Job priority")
    tags: List[str] = Field(default_factory=list, description="Job tags")


class BatchJobProgress(BaseModel):
    """Progress of a batch job"""
    job_id: str = Field(..., description="Job identifier")
    status: BatchJobStatus = Field(..., description="Current status")
    
    # Progress tracking
    total_items: int = Field(..., description="Total items to process")
    processed_items: int = Field(default=0, description="Items processed")
    failed_items: int = Field(default=0, description="Items that failed")
    progress_percentage: float = Field(default=0.0, description="Progress percentage")
    
    # Timing
    started_at: Optional[datetime] = Field(None, description="Start time")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    
    # Results preview
    sample_results: List[Dict[str, Any]] = Field(default_factory=list, description="Sample results")
    error_summary: Optional[str] = Field(None, description="Error summary if applicable")


class LabelingJobRequest(BaseModel):
    """Request for batch labeling job using LLM"""
    job_id: str = Field(..., description="Unique job identifier")
    
    # Data to label
    items: List[Dict[str, Any]] = Field(..., description="Items to label")
    item_type: str = Field(..., description="Type of items (e.g., 'trade', 'transaction')")
    
    # Labeling configuration
    labels: List[str] = Field(..., description="Possible labels")
    label_descriptions: Dict[str, str] = Field(default_factory=dict, description="Label descriptions")
    context: Optional[str] = Field(None, description="Labeling context")
    
    # Quality control
    confidence_threshold: float = Field(default=0.8, description="Minimum confidence for auto-labeling")
    human_review_required: bool = Field(default=True, description="Whether human review is needed")
    sample_for_validation: float = Field(default=0.1, description="Fraction to sample for validation")
    
    # Model configuration
    model_name: Optional[str] = Field(None, description="Specific model to use")
    few_shot_examples: List[Dict[str, Any]] = Field(default_factory=list, description="Few-shot examples")


# ==================== Search and Similarity Schemas ====================

class SimilaritySearchRequest(BaseModel):
    """Request for similarity search using embeddings"""
    query_text: str = Field(..., description="Text to search for similar items")
    search_type: Literal["trades", "logs", "general"] = Field(..., description="Type of items to search")
    
    # Search parameters
    top_k: int = Field(default=10, description="Number of results to return")
    similarity_threshold: float = Field(default=0.7, description="Minimum similarity score")
    
    # Filters
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range filter")
    symbol_filter: Optional[str] = Field(None, description="Symbol filter")
    additional_filters: Dict[str, Any] = Field(default_factory=dict, description="Additional filters")
    
    # Options
    include_embeddings: bool = Field(default=False, description="Include embedding vectors in response")
    explain_similarity: bool = Field(default=True, description="Include similarity explanations")


class SimilaritySearchResult(BaseModel):
    """Result from similarity search"""
    item_id: str = Field(..., description="Item identifier")
    content: str = Field(..., description="Item content")
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    
    # Metadata
    item_type: str = Field(..., description="Type of item")
    timestamp: Optional[datetime] = Field(None, description="Item timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Optional fields
    embedding: Optional[List[float]] = Field(None, description="Embedding vector if requested")
    explanation: Optional[str] = Field(None, description="Similarity explanation")


class SimilaritySearchResponse(BaseModel):
    """Response from similarity search"""
    query: str = Field(..., description="Original query")
    total_results: int = Field(..., description="Total matching results")
    results: List[SimilaritySearchResult] = Field(..., description="Search results")
    
    # Search metadata
    search_time_ms: float = Field(..., description="Search time in milliseconds")
    embedding_model: str = Field(..., description="Embedding model used")
    parameters: Dict[str, Any] = Field(..., description="Search parameters used")
    
    # Query analysis
    query_embedding_time_ms: Optional[float] = Field(None, description="Time to generate query embedding")
    total_items_searched: Optional[int] = Field(None, description="Total items in search index")


# ==================== Configuration Schemas ====================

class MLModelConfig(BaseModel):
    """Configuration for ML models"""
    model_name: str = Field(..., description="Model name")
    model_type: ModelType = Field(..., description="Model type")
    version: str = Field(default="1.0", description="Model version")
    
    # Training configuration
    hyperparameters: Dict[str, Any] = Field(default_factory=dict, description="Model hyperparameters")
    training_config: Dict[str, Any] = Field(default_factory=dict, description="Training configuration")
    
    # Performance requirements
    max_inference_time_ms: Optional[int] = Field(None, description="Maximum inference time")
    min_accuracy: Optional[float] = Field(None, description="Minimum required accuracy")
    
    # Resource requirements
    memory_limit_mb: Optional[int] = Field(None, description="Memory limit")
    cpu_cores: Optional[int] = Field(None, description="CPU cores required")
    gpu_required: bool = Field(default=False, description="Whether GPU is required")


class AutoMLConfig(BaseModel):
    """Configuration for AutoML experiments"""
    experiment_name: str = Field(..., description="AutoML experiment name")
    problem_type: ProblemType = Field(..., description="Type of ML problem")
    
    # Data configuration
    target_column: str = Field(..., description="Target variable column")
    feature_columns: List[str] = Field(..., description="Feature columns")
    categorical_columns: List[str] = Field(default_factory=list, description="Categorical columns")
    
    # AutoML settings
    max_models: int = Field(default=20, description="Maximum number of models to try")
    max_runtime_hours: int = Field(default=2, description="Maximum runtime in hours")
    metric_to_optimize: str = Field(..., description="Metric to optimize")
    
    # Advanced settings
    ensemble_methods: bool = Field(default=True, description="Whether to use ensemble methods")
    feature_selection: bool = Field(default=True, description="Whether to perform feature selection")
    early_stopping: bool = Field(default=True, description="Whether to use early stopping")
    
    # Cross-validation
    cv_folds: int = Field(default=5, description="Cross-validation folds")
    validation_strategy: str = Field(default="stratified", description="Validation strategy")


# ==================== Response Schemas ====================

class StandardResponse(BaseModel):
    """Standard API response format"""
    success: bool = Field(..., description="Whether operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class PaginatedResponse(BaseModel):
    """Paginated response format"""
    items: List[Any] = Field(..., description="Response items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")