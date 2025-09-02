"""
Database model for ML experiments and A/B testing
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from app.models.base import BaseModel
from app.services.schemas import ExperimentStatus, ProblemType


class Experiment(BaseModel):
    """ML Experiment model for tracking experiments and A/B tests"""
    
    __tablename__ = "experiments"
    
    # Basic information
    experiment_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Experiment configuration
    problem_type = Column(SQLEnum(ProblemType), nullable=False)
    status = Column(SQLEnum(ExperimentStatus), nullable=False, default=ExperimentStatus.PLANNED)
    objective = Column(Text)
    
    # Data and features
    data_sources = Column(JSON)  # List of data sources
    feature_columns = Column(JSON)  # List of feature columns
    target_variable = Column(String(100))
    date_range = Column(JSON)  # {"start": "2024-01-01", "end": "2024-12-31"}
    
    # Model configuration
    algorithms = Column(JSON)  # List of AlgorithmConfig objects
    feature_engineering = Column(JSON)  # List of FeatureConfig objects
    preprocessing_steps = Column(JSON)  # List of preprocessing steps
    
    # Evaluation configuration
    evaluation_metrics = Column(JSON)  # List of EvaluationMetric objects
    validation_strategy = Column(String(100), default="time_series_split")
    test_size = Column(Float, default=0.2)
    
    # Resource constraints
    max_training_time_hours = Column(Integer)
    max_memory_gb = Column(Integer)
    compute_requirements = Column(String(50))  # "cpu" or "gpu"
    
    # Success criteria
    success_criteria = Column(JSON)  # List of success criteria
    minimum_performance = Column(JSON)  # Dict of metric thresholds
    
    # Results
    metrics = Column(JSON)  # Performance metrics
    best_model = Column(String(100))
    model_performance = Column(JSON)  # Performance by model
    feature_importance = Column(JSON)  # Feature importance scores
    
    # Training details
    training_duration_seconds = Column(Float)
    total_samples = Column(Integer)
    model_path = Column(String(500))  # Path to saved model
    artifacts = Column(JSON)  # Paths to other artifacts
    
    # Timeline and metadata
    estimated_duration_hours = Column(Integer)
    priority = Column(Integer, default=1)
    tags = Column(JSON)  # List of tags
    
    # Execution tracking
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    logs = Column(JSON)  # List of log entries
    
    # Planning metadata
    planned_by = Column(String(100))
    planned_at = Column(DateTime, default=func.now())
    auto_generated = Column(Boolean, default=False)
    
    # A/B testing specific fields
    variant_name = Column(String(100))  # For A/B test variants
    parent_experiment_id = Column(String(100))  # Reference to parent experiment
    control_group = Column(Boolean, default=False)  # Whether this is the control group
    traffic_allocation = Column(Float)  # Percentage of traffic allocated
    
    def __repr__(self):
        return f"<Experiment(id={self.experiment_id}, name={self.name}, status={self.status})>"
    
    @property
    def is_completed(self) -> bool:
        """Check if experiment is completed"""
        return self.status in [ExperimentStatus.COMPLETED, ExperimentStatus.FAILED, ExperimentStatus.CANCELLED]
    
    @property
    def duration_minutes(self) -> float:
        """Get experiment duration in minutes"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() / 60
        return 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate based on success criteria"""
        if not self.metrics or not self.success_criteria:
            return 0.0
        
        met_criteria = 0
        total_criteria = len(self.success_criteria)
        
        for criterion in self.success_criteria:
            # Simple check - in practice, this would be more sophisticated
            if any(criterion.lower() in str(self.metrics).lower() for criterion in self.success_criteria):
                met_criteria += 1
        
        return met_criteria / total_criteria if total_criteria > 0 else 0.0