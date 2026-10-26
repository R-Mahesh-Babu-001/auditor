from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    """
    return {
        "status": "ok",
        "service": "auditor-copilot-backend",
        "providers": {
            "azure_openai_configured": all([
                settings.AZURE_OPENAI_4o_MINI_API_KEY,
                settings.AZURE_OPENAI_4o_MINI_ENDPOINT,
                settings.AZURE_OPENAI_4o_MINI_API_VERSION
            ]),
            "aws_bedrock_configured": all([
                settings.AWS_REGION,
                settings.AWS_ACCESS_KEY_ID,
                settings.AWS_SECRET_ACCESS_KEY
            ])
        }
    }

"""
Health router for service and provider status checks.
"""