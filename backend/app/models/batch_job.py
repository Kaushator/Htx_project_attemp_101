"""
Database model for batch jobs and processing tasks
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from app.models.base import BaseModel
from app.services.schemas import BatchJobStatus


class BatchJob(BaseModel):
    """Batch Job model for tracking long-running processing tasks"""
    
    __tablename__ = "batch_jobs"
    
    # Basic information
    job_id = Column(String(100), unique=True, nullable=False, index=True)
    job_type = Column(String(100), nullable=False)  # "labeling", "analysis", "prediction", etc.
    description = Column(Text)
    status = Column(SQLEnum(BatchJobStatus), nullable=False, default=BatchJobStatus.PENDING)
    
    # Input configuration
    input_source = Column(String(500))  # Source of input data
    input_data_size = Column(Integer)  # Number of input items
    input_data_hash = Column(String(64))  # Hash of input data for deduplication
    
    # Processing configuration
    batch_size = Column(Integer, default=100)
    parallel_workers = Column(Integer, default=1)
    timeout_seconds = Column(Integer)
    parameters = Column(JSON)  # Job-specific parameters
    context = Column(Text)  # Additional context for processing
    
    # Progress tracking
    total_items = Column(Integer, nullable=False)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)
    
    # Results
    output_data = Column(JSON)  # Processed results (for small jobs)
    output_location = Column(String(500))  # Path to results file (for large jobs)
    sample_results = Column(JSON)  # Sample of results for preview
    
    # Quality metrics
    success_rate = Column(Float)  # Percentage of successful items
    average_confidence = Column(Float)  # Average confidence score
    quality_score = Column(Float)  # Overall quality assessment
    
    # Error tracking
    error_summary = Column(Text)
    failed_items_sample = Column(JSON)  # Sample of failed items for debugging
    error_categories = Column(JSON)  # Categorized error counts
    
    # Resource usage
    cpu_time_seconds = Column(Float)
    memory_peak_mb = Column(Float)
    api_calls_made = Column(Integer)  # For LLM-based jobs
    tokens_used = Column(Integer)  # For LLM-based jobs
    cost_estimate_usd = Column(Float)  # Estimated cost
    
    # Timeline
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_completion = Column(DateTime)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Metadata
    created_by = Column(String(100))
    priority = Column(Integer, default=1)
    tags = Column(JSON)  # List of tags
    parent_job_id = Column(String(100))  # For job chains/dependencies
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Model-specific fields (for ML jobs)
    model_name = Column(String(100))
    model_version = Column(String(50))
    confidence_threshold = Column(Float)
    human_review_required = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<BatchJob(id={self.job_id}, type={self.job_type}, status={self.status})>"
    
    @property
    def is_completed(self) -> bool:
        """Check if job is completed"""
        return self.status in [BatchJobStatus.COMPLETED, BatchJobStatus.FAILED, BatchJobStatus.CANCELLED]
    
    @property
    def duration_minutes(self) -> float:
        """Get job duration in minutes"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() / 60
        elif self.started_at:
            return (func.now() - self.started_at).total_seconds() / 60
        return 0
    
    @property
    def estimated_time_remaining_minutes(self) -> float:
        """Estimate time remaining based on current progress"""
        if self.progress_percentage <= 0 or not self.started_at:
            return 0
        
        elapsed_seconds = (func.now() - self.started_at).total_seconds()
        total_estimated_seconds = elapsed_seconds / (self.progress_percentage / 100)
        remaining_seconds = total_estimated_seconds - elapsed_seconds
        
        return max(0, remaining_seconds / 60)
    
    @property
    def throughput_items_per_minute(self) -> float:
        """Calculate processing throughput"""
        if not self.started_at or self.processed_items <= 0:
            return 0
        
        elapsed_minutes = (func.now() - self.started_at).total_seconds() / 60
        return self.processed_items / elapsed_minutes if elapsed_minutes > 0 else 0
    
    def update_progress(self, processed: int, failed: int = 0):
        """Update job progress"""
        self.processed_items = processed
        self.failed_items = failed
        self.progress_percentage = (processed + failed) / self.total_items * 100 if self.total_items > 0 else 0
        self.success_rate = processed / (processed + failed) * 100 if (processed + failed) > 0 else 0
        self.last_updated = func.now()
        
        # Update estimated completion
        if self.progress_percentage > 0 and self.started_at:
            elapsed_seconds = (func.now() - self.started_at).total_seconds()
            total_estimated_seconds = elapsed_seconds / (self.progress_percentage / 100)
            self.estimated_completion = self.started_at + func.timedelta(seconds=total_estimated_seconds)


class LabelingJob(BaseModel):
    """Specialized batch job for LLM-based labeling tasks"""
    
    __tablename__ = "labeling_jobs"
    
    # Reference to parent batch job
    batch_job_id = Column(String(100), nullable=False, index=True)
    
    # Labeling-specific configuration
    item_type = Column(String(100), nullable=False)  # "trade", "transaction", "log", etc.
    labels = Column(JSON, nullable=False)  # List of possible labels
    label_descriptions = Column(JSON)  # Dict of label descriptions
    context = Column(Text)  # Labeling context
    
    # Quality control
    confidence_threshold = Column(Float, default=0.8)
    human_review_required = Column(Boolean, default=True)
    sample_for_validation = Column(Float, default=0.1)
    validation_results = Column(JSON)  # Results from human validation
    
    # Model configuration
    model_name = Column(String(100))
    few_shot_examples = Column(JSON)  # List of few-shot examples
    temperature = Column(Float, default=0.1)
    max_tokens = Column(Integer, default=1000)
    
    # Results analysis
    label_distribution = Column(JSON)  # Count of each label assigned
    confidence_distribution = Column(JSON)  # Distribution of confidence scores
    low_confidence_items = Column(JSON)  # Items with confidence below threshold
    consensus_analysis = Column(JSON)  # Analysis of labeling consensus
    
    # Human review tracking
    items_reviewed = Column(Integer, default=0)
    review_corrections = Column(Integer, default=0)
    reviewer_agreement_rate = Column(Float)  # Agreement between AI and human
    
    def __repr__(self):
        return f"<LabelingJob(batch_job_id={self.batch_job_id}, item_type={self.item_type})>"
    
    @property
    def review_completion_rate(self) -> float:
        """Calculate human review completion rate"""
        if not hasattr(self, '_parent_job'):
            return 0
        
        total_for_review = int(self._parent_job.total_items * self.sample_for_validation)
        return self.items_reviewed / total_for_review * 100 if total_for_review > 0 else 0
    
    @property
    def quality_metrics(self) -> dict:
        """Get comprehensive quality metrics"""
        return {
            "average_confidence": self.confidence_distribution.get("mean", 0) if self.confidence_distribution else 0,
            "high_confidence_rate": len([item for item in (self.low_confidence_items or []) 
                                       if item.get("confidence", 0) >= self.confidence_threshold]) / len(self.low_confidence_items or [1]) * 100,
            "reviewer_agreement_rate": self.reviewer_agreement_rate or 0,
            "correction_rate": self.review_corrections / self.items_reviewed * 100 if self.items_reviewed > 0 else 0
        }