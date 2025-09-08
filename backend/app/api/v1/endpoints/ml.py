"""
ML Analytics API Endpoints
Provides endpoints for ML planning, batch labeling, and similarity search
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime

from app.db.session import get_db, AsyncSessionLocal
from app.services.openai_client import get_openai_client, JSONModeRequest, BatchLabelRequest
from app.services.embedding_service import get_embedding_service
from app.services.schemas import (
    ExperimentPlan, ExperimentResult, BatchJobRequest, LabelingJobRequest,
    SimilaritySearchRequest, SimilaritySearchResponse, StandardResponse,
    ExperimentStatus, BatchJobStatus
)
from app.models.experiment import Experiment
from app.models.batch_job import BatchJob, LabelingJob
from app.services.enhanced_risk_metrics import get_risk_metrics_service
from app.services.fingpt_service import get_fingpt_service
from app.services.mistral_service import get_mistral_service
from app.core.config import settings

router = APIRouter()


@router.post("/plan", response_model=StandardResponse)
async def plan_ml_experiment(
    experiment_description: str,
    available_data: Dict[str, Any],
    constraints: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Plan an ML experiment using OpenAI
    
    Args:
        experiment_description: What the experiment should accomplish
        available_data: Description of available data and features
        constraints: Resource and time constraints
        
    Returns:
        Generated experiment plan
    """
    try:
        openai_client = await get_openai_client()
        
        # Generate experiment plan using OpenAI
        plan_response = await openai_client.plan_ml_experiment(
            experiment_description, available_data, constraints
        )
        
        if not plan_response["success"]:
            raise HTTPException(status_code=500, detail=plan_response["error"])
        
        plan_data = plan_response["data"]
        
        # Create experiment record in database
        experiment = Experiment(
            experiment_id=plan_data["experiment_id"],
            name=plan_data["experiment_name"],
            description=experiment_description,
            problem_type=plan_data["problem_type"],
            status=ExperimentStatus.PLANNED,
            objective=experiment_description,
            data_sources=available_data.get("sources", []),
            feature_columns=available_data.get("features", []),
            algorithms=plan_data["algorithms"],
            evaluation_metrics=[{"name": metric, "weight": 1.0} for metric in plan_data["evaluation_metrics"]],
            success_criteria=plan_data["success_criteria"],
            estimated_duration_hours=plan_data.get("timeline_weeks", 1) * 40,  # Convert weeks to hours
            planned_by="ai_planner",
            auto_generated=True,
            tags=["auto_planned", "openai"]
        )
        
        db.add(experiment)
        await db.commit()
        await db.refresh(experiment)
        
        return StandardResponse(
            success=True,
            message="ML experiment plan generated successfully",
            data={
                "experiment_id": experiment.experiment_id,
                "plan": plan_data,
                "database_id": experiment.id
            },
            metadata={
                "model_used": plan_response.get("model", "unknown"),
                "tokens_used": plan_response.get("tokens_used", 0),
                "constraints": constraints
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to plan experiment: {str(e)}")


@router.get("/experiments", response_model=List[ExperimentPlan])
async def list_experiments(
    status: Optional[ExperimentStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List ML experiments with optional filtering"""
    try:
        from sqlalchemy import select
        
        query = select(Experiment)
        if status:
            query = query.where(Experiment.status == status)
        
        query = query.offset(offset).limit(limit).order_by(Experiment.created_at.desc())
        
        result = await db.execute(query)
        experiments = result.scalars().all()
        
        # Convert to response format
        experiment_plans = []
        for exp in experiments:
            plan = ExperimentPlan(
                experiment_id=exp.experiment_id,
                name=exp.name,
                description=exp.description or "",
                problem_type=exp.problem_type,
                objective=exp.objective or "",
                data_sources=exp.data_sources or [],
                feature_columns=exp.feature_columns or [],
                algorithms=exp.algorithms or [],
                evaluation_metrics=exp.evaluation_metrics or [],
                success_criteria=exp.success_criteria or [],
                planned_by=exp.planned_by,
                planned_at=exp.planned_at,
                auto_generated=exp.auto_generated,
                tags=exp.tags or []
            )
            experiment_plans.append(plan)
        
        return experiment_plans
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list experiments: {str(e)}")


@router.get("/experiments/{experiment_id}", response_model=ExperimentResult)
async def get_experiment(
    experiment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get specific experiment details and results"""
    try:
        from sqlalchemy import select
        
        result = await db.execute(
            select(Experiment).where(Experiment.experiment_id == experiment_id)
        )
        experiment = result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        experiment_result = ExperimentResult(
            experiment_id=experiment.experiment_id,
            status=experiment.status,
            metrics=experiment.metrics or {},
            best_model=experiment.best_model,
            model_performance=experiment.model_performance or {},
            training_duration_seconds=experiment.training_duration_seconds,
            total_samples=experiment.total_samples,
            feature_importance=experiment.feature_importance,
            model_path=experiment.model_path,
            artifacts=experiment.artifacts or {},
            started_at=experiment.started_at,
            completed_at=experiment.completed_at,
            error_message=experiment.error_message,
            logs=experiment.logs or []
        )
        
        return experiment_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get experiment: {str(e)}")


@router.post("/batch_label", response_model=StandardResponse)
async def create_batch_labeling_job(
    labeling_request: LabelingJobRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a batch labeling job using LLM
    
    Args:
        labeling_request: Labeling job configuration
        background_tasks: FastAPI background tasks
        
    Returns:
        Job creation response
    """
    try:
        # Create batch job record
        batch_job = BatchJob(
            job_id=labeling_request.job_id,
            job_type="labeling",
            description=f"Batch labeling of {labeling_request.item_type} items",
            status=BatchJobStatus.PENDING,
            total_items=len(labeling_request.items),
            parameters={
                "labels": labeling_request.labels,
                "confidence_threshold": labeling_request.confidence_threshold,
                "model_name": labeling_request.model_name
            },
            context=labeling_request.context,
            model_name=labeling_request.model_name,
            confidence_threshold=labeling_request.confidence_threshold,
            human_review_required=labeling_request.human_review_required,
            created_by="api_user"
        )
        
        # Create labeling job record
        labeling_job = LabelingJob(
            batch_job_id=labeling_request.job_id,
            item_type=labeling_request.item_type,
            labels=labeling_request.labels,
            label_descriptions=labeling_request.label_descriptions,
            context=labeling_request.context,
            confidence_threshold=labeling_request.confidence_threshold,
            human_review_required=labeling_request.human_review_required,
            sample_for_validation=labeling_request.sample_for_validation,
            model_name=labeling_request.model_name,
            few_shot_examples=labeling_request.few_shot_examples
        )
        
        db.add(batch_job)
        db.add(labeling_job)
        await db.commit()
        
        # Schedule background processing
        background_tasks.add_task(
            process_labeling_job, 
            labeling_request.job_id, 
            labeling_request.items
        )
        
        return StandardResponse(
            success=True,
            message="Batch labeling job created successfully",
            data={
                "job_id": labeling_request.job_id,
                "total_items": len(labeling_request.items),
                "estimated_time_minutes": len(labeling_request.items) * 0.5,  # Rough estimate
                "status": "pending"
            },
            metadata={
                "job_type": "labeling",
                "item_type": labeling_request.item_type,
                "labels": labeling_request.labels
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create labeling job: {str(e)}")


@router.get("/batch_jobs/{job_id}/status")
async def get_batch_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get status of a batch job"""
    try:
        from sqlalchemy import select
        
        result = await db.execute(
            select(BatchJob).where(BatchJob.job_id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "progress_percentage": job.progress_percentage,
            "processed_items": job.processed_items,
            "total_items": job.total_items,
            "failed_items": job.failed_items,
            "success_rate": job.success_rate,
            "estimated_completion": job.estimated_completion,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "error_summary": job.error_summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@router.post("/search/similar", response_model=SimilaritySearchResponse)
async def similarity_search(
    search_request: SimilaritySearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Perform similarity search using embeddings
    
    Args:
        search_request: Search parameters
        
    Returns:
        Similar items with similarity scores
    """
    try:
        embedding_service = await get_embedding_service()
        
        response = await embedding_service.similarity_search(db, search_request)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity search failed: {str(e)}")


@router.post("/embeddings/compute")
async def compute_embeddings(
    content_type: str,
    symbol: Optional[str] = None,
    limit: Optional[int] = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Compute embeddings for existing data
    
    Args:
        content_type: Type of content to embed ("trades", "logs", etc.)
        symbol: Optional symbol filter
        limit: Maximum number of items to process
        
    Returns:
        Processing results
    """
    try:
        embedding_service = await get_embedding_service()
        
        if content_type == "trades":
            result = await embedding_service.embed_trades(db, limit, symbol)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported content type: {content_type}")
        
        return StandardResponse(
            success=True,
            message="Embedding computation completed",
            data=result,
            metadata={
                "content_type": content_type,
                "symbol": symbol,
                "limit": limit
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute embeddings: {str(e)}")


@router.get("/health")
async def ml_health_check():
    """Health check for ML services"""
    try:
        # Check OpenAI connectivity
        openai_client = await get_openai_client()
        openai_health = await openai_client.health_check()
        
        # Check embedding service
        embedding_service = await get_embedding_service()
        
        # Check LLM services
        fingpt_service = await get_fingpt_service()
        mistral_service = await get_mistral_service()
        
        return {
            "status": "healthy",
            "services": {
                "openai": openai_health,
                "embeddings": {"status": "available"},
                "ml_analytics": {"status": "available"},
                "fingpt": fingpt_service.get_model_info(),
                "mistral": mistral_service.get_model_info(),
                "risk_metrics": {"status": "available"}
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/risk_analysis")
async def calculate_risk_metrics(
    symbol: Optional[str] = None,
    days_lookback: int = 365,
    db: AsyncSession = Depends(get_db)
):
    """Calculate comprehensive risk metrics"""
    try:
        risk_service = await get_risk_metrics_service()
        
        metrics = await risk_service.calculate_comprehensive_risk_metrics(
            db, symbol, days_lookback
        )
        
        return StandardResponse(
            success=True,
            message="Risk metrics calculated successfully",
            data=metrics,
            metadata={
                "symbol": symbol,
                "lookback_days": days_lookback
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")


@router.post("/fingpt/analyze_trade")
async def fingpt_analyze_trade(
    trade_data: Dict[str, Any],
    context: Optional[str] = None
):
    """Analyze trade using FinGPT"""
    try:
        fingpt_service = await get_fingpt_service()
        
        analysis = await fingpt_service.analyze_trade_sentiment(trade_data, context)
        
        return StandardResponse(
            success=True,
            message="Trade analysis completed",
            data=analysis
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FinGPT analysis failed: {str(e)}")


@router.post("/mistral/trading_signals")
async def mistral_generate_signals(
    market_data: Dict[str, Any],
    indicators: List[str],
    timeframe: str = "1H"
):
    """Generate trading signals using Mistral"""
    try:
        mistral_service = await get_mistral_service()
        
        signals = await mistral_service.generate_trading_signals(
            market_data, indicators, timeframe
        )
        
        return StandardResponse(
            success=True,
            message="Trading signals generated",
            data=signals
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signal generation failed: {str(e)}")


# Background task functions
async def process_labeling_job(job_id: str, items: List[Dict[str, Any]]):
    """Background task to process labeling job"""
    try:
        from app.db.session import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            # Update job status to processing
            from sqlalchemy import select, update
            
            await db.execute(
                update(BatchJob)
                .where(BatchJob.job_id == job_id)
                .values(
                    status=BatchJobStatus.PROCESSING,
                    started_at=datetime.utcnow()
                )
            )
            await db.commit()
            
            # Get OpenAI client
            openai_client = await get_openai_client()
            
            # Get job configuration
            job_result = await db.execute(
                select(LabelingJob).where(LabelingJob.batch_job_id == job_id)
            )
            labeling_job = job_result.scalar_one()
            
            # Process items in batches
            batch_size = 50  # Adjust based on API limits
            processed = 0
            failed = 0
            all_results = []
            
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                
                # Create batch labeling request
                batch_request = BatchLabelRequest(
                    items=batch,
                    labels=labeling_job.labels,
                    context=labeling_job.context,
                    confidence_threshold=labeling_job.confidence_threshold
                )
                
                # Process batch
                response = await openai_client.batch_label(batch_request)
                
                if response["success"]:
                    all_results.extend(response["labels"])
                    processed += len(batch)
                else:
                    failed += len(batch)
                
                # Update progress
                await db.execute(
                    update(BatchJob)
                    .where(BatchJob.job_id == job_id)
                    .values(
                        processed_items=processed,
                        failed_items=failed,
                        progress_percentage=(processed + failed) / len(items) * 100
                    )
                )
                await db.commit()
            
            # Mark job as completed
            await db.execute(
                update(BatchJob)
                .where(BatchJob.job_id == job_id)
                .values(
                    status=BatchJobStatus.COMPLETED,
                    completed_at=datetime.utcnow(),
                    output_data=all_results[:100],  # Store sample
                    success_rate=processed / len(items) * 100
                )
            )
            await db.commit()
            
    except Exception as e:
        # Mark job as failed
        async with AsyncSessionLocal() as db:
            from sqlalchemy import update
            await db.execute(
                update(BatchJob)
                .where(BatchJob.job_id == job_id)
                .values(
                    status=BatchJobStatus.FAILED,
                    completed_at=datetime.utcnow(),
                    error_summary=str(e)
                )
            )
            await db.commit()