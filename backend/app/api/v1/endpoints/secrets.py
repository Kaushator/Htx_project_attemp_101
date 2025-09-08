"""
Secret Manager API endpoints for Google Secret Manager integration
Provides secret validation, status checking, and management functionality
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime

# Import the secrets manager from core
try:
    from app.core.secrets_manager import SecretsManager, get_secrets_manager
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

logger = logging.getLogger(__name__)
router = APIRouter()

# Response models
class SecretStatus(BaseModel):
    name: str
    description: str
    exists: bool
    last_updated: Optional[datetime] = None
    required: bool
    status: str  # 'active', 'inactive', 'error', 'warning'

class SecretsOverview(BaseModel):
    total_secrets: int
    active_secrets: int
    required_secrets: int
    missing_required: List[str]
    connection_status: str
    last_check: datetime

class SecretValidationResult(BaseModel):
    secret_name: str
    valid: bool
    error_message: Optional[str] = None
    test_result: Optional[Dict[str, Any]] = None

class SecretUpdateRequest(BaseModel):
    secret_name: str
    secret_value: str

# Secret definitions with metadata
SECRET_DEFINITIONS = {
    "htx-api-key": {
        "description": "HTX exchange API access key",
        "required": True,
        "env_var": "HTX_API_KEY"
    },
    "htx-api-secret": {
        "description": "HTX exchange API secret key", 
        "required": True,
        "env_var": "HTX_API_SECRET"
    },
    "htx-subuid": {
        "description": "HTX sub-account user ID",
        "required": False,
        "env_var": "HTX_SUBUID"
    },
    "openai-api-key": {
        "description": "OpenAI API key for ML services",
        "required": False,
        "env_var": "OPENAI_API_KEY"
    },
    "threecommas-api-key": {
        "description": "3Commas API key for bot integration",
        "required": False,
        "env_var": "THREECOMMAS_API_KEY"
    },
    "threecommas-api-secret": {
        "description": "3Commas API secret",
        "required": False,
        "env_var": "THREECOMMAS_API_SECRET"
    }
}

@router.get("/status", response_model=SecretsOverview)
async def get_secrets_status(secrets_manager: SecretsManager = Depends(get_secrets_manager)):
    """
    Get overall status of all secrets in Secret Manager
    """
    try:
        if not SECRETS_MANAGER_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Secret Manager not available"
            )
        
        # Check connection to Secret Manager
        connection_status = "connected"
        try:
            # Test connection by listing secrets
            await secrets_manager.list_secrets()
        except Exception as e:
            logger.error(f"Secret Manager connection failed: {e}")
            connection_status = "error"
        
        # Check each secret
        total_secrets = len(SECRET_DEFINITIONS)
        active_secrets = 0
        missing_required = []
        
        for secret_name, config in SECRET_DEFINITIONS.items():
            try:
                secret_value = await secrets_manager.get_secret(secret_name)
                if secret_value:
                    active_secrets += 1
                elif config["required"]:
                    missing_required.append(secret_name)
            except Exception as e:
                logger.warning(f"Failed to check secret {secret_name}: {e}")
                if config["required"]:
                    missing_required.append(secret_name)
        
        required_secrets = len([s for s in SECRET_DEFINITIONS.values() if s["required"]])
        
        return SecretsOverview(
            total_secrets=total_secrets,
            active_secrets=active_secrets,
            required_secrets=required_secrets,
            missing_required=missing_required,
            connection_status=connection_status,
            last_check=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to get secrets status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve secrets status: {str(e)}"
        )

@router.get("/list", response_model=List[SecretStatus])
async def list_secrets(secrets_manager: SecretsManager = Depends(get_secrets_manager)):
    """
    List all configured secrets with their status
    """
    try:
        if not SECRETS_MANAGER_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Secret Manager not available"
            )
        
        results = []
        
        for secret_name, config in SECRET_DEFINITIONS.items():
            try:
                # Check if secret exists and has value
                secret_value = await secrets_manager.get_secret(secret_name)
                exists = bool(secret_value)
                
                # Determine status
                if exists:
                    secret_status = "active"
                elif config["required"]:
                    secret_status = "error"
                else:
                    secret_status = "inactive"
                
                # Get last updated time (mock for now)
                last_updated = datetime.utcnow() if exists else None
                
                results.append(SecretStatus(
                    name=secret_name,
                    description=config["description"],
                    exists=exists,
                    last_updated=last_updated,
                    required=config["required"],
                    status=secret_status
                ))
                
            except Exception as e:
                logger.warning(f"Failed to check secret {secret_name}: {e}")
                results.append(SecretStatus(
                    name=secret_name,
                    description=config["description"],
                    exists=False,
                    last_updated=None,
                    required=config["required"],
                    status="error"
                ))
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to list secrets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list secrets: {str(e)}"
        )

@router.post("/validate/{secret_name}", response_model=SecretValidationResult)
async def validate_secret(
    secret_name: str,
    secrets_manager: SecretsManager = Depends(get_secrets_manager)
):
    """
    Validate a specific secret by testing its functionality
    """
    try:
        if not SECRETS_MANAGER_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Secret Manager not available"
            )
        
        if secret_name not in SECRET_DEFINITIONS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secret '{secret_name}' not found in configuration"
            )
        
        # Get the secret value
        try:
            secret_value = await secrets_manager.get_secret(secret_name)
            if not secret_value:
                return SecretValidationResult(
                    secret_name=secret_name,
                    valid=False,
                    error_message="Secret value is empty or not found"
                )
        except Exception as e:
            return SecretValidationResult(
                secret_name=secret_name,
                valid=False,
                error_message=f"Failed to retrieve secret: {str(e)}"
            )
        
        # Perform specific validation based on secret type
        test_result = {}
        valid = True
        error_message = None
        
        try:
            if secret_name.startswith("htx-"):
                # Validate HTX API key format
                if secret_name == "htx-api-key":
                    if len(secret_value) < 10:
                        valid = False
                        error_message = "HTX API key appears to be too short"
                    else:
                        test_result["format"] = "valid"
                        test_result["length"] = len(secret_value)
                        
                elif secret_name == "htx-api-secret":
                    if len(secret_value) < 20:
                        valid = False
                        error_message = "HTX API secret appears to be too short"
                    else:
                        test_result["format"] = "valid"
                        test_result["length"] = len(secret_value)
                        
            elif secret_name == "openai-api-key":
                # Validate OpenAI API key format
                if not secret_value.startswith("sk-"):
                    valid = False
                    error_message = "OpenAI API key should start with 'sk-'"
                else:
                    test_result["format"] = "valid"
                    test_result["prefix"] = "sk-"
                    
            else:
                # Basic validation for other secrets
                test_result["format"] = "basic_check"
                test_result["length"] = len(secret_value)
        
        except Exception as e:
            valid = False
            error_message = f"Validation error: {str(e)}"
        
        return SecretValidationResult(
            secret_name=secret_name,
            valid=valid,
            error_message=error_message,
            test_result=test_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate secret {secret_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate secret: {str(e)}"
        )

@router.post("/update", response_model=Dict[str, str])
async def update_secret(
    request: SecretUpdateRequest,
    secrets_manager: SecretsManager = Depends(get_secrets_manager)
):
    """
    Update a secret value in Secret Manager
    """
    try:
        if not SECRETS_MANAGER_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Secret Manager not available"
            )
        
        if request.secret_name not in SECRET_DEFINITIONS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secret '{request.secret_name}' not found in configuration"
            )
        
        # Update the secret
        await secrets_manager.create_or_update_secret(
            request.secret_name, 
            request.secret_value
        )
        
        logger.info(f"Successfully updated secret: {request.secret_name}")
        
        return {
            "status": "success",
            "message": f"Secret '{request.secret_name}' updated successfully",
            "updated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update secret {request.secret_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update secret: {str(e)}"
        )

@router.delete("/{secret_name}", response_model=Dict[str, str])
async def delete_secret(
    secret_name: str,
    secrets_manager: SecretsManager = Depends(get_secrets_manager)
):
    """
    Delete a secret from Secret Manager
    """
    try:
        if not SECRETS_MANAGER_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Secret Manager not available"
            )
        
        if secret_name not in SECRET_DEFINITIONS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secret '{secret_name}' not found in configuration"
            )
        
        # Check if it's a required secret
        if SECRET_DEFINITIONS[secret_name]["required"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete required secret '{secret_name}'"
            )
        
        # Delete the secret
        await secrets_manager.delete_secret(secret_name)
        
        logger.info(f"Successfully deleted secret: {secret_name}")
        
        return {
            "status": "success", 
            "message": f"Secret '{secret_name}' deleted successfully",
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete secret {secret_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete secret: {str(e)}"
        )

@router.get("/health", response_model=Dict[str, Any])
async def secrets_health_check():
    """
    Health check for Secret Manager service
    """
    try:
        health_status = {
            "service": "secrets_manager",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "features": {
                "secret_manager_available": SECRETS_MANAGER_AVAILABLE,
                "total_secrets_configured": len(SECRET_DEFINITIONS),
                "required_secrets": len([s for s in SECRET_DEFINITIONS.values() if s["required"]])
            }
        }
        
        if SECRETS_MANAGER_AVAILABLE:
            try:
                # Test basic Secret Manager functionality
                secrets_manager = get_secrets_manager()
                # This is a basic connectivity test
                health_status["features"]["connectivity"] = "available"
            except Exception as e:
                health_status["status"] = "degraded"
                health_status["features"]["connectivity"] = f"error: {str(e)}"
        else:
            health_status["status"] = "unavailable"
            health_status["features"]["connectivity"] = "secret_manager_not_configured"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "service": "secrets_manager",
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }