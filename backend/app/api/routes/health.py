from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "success": True,
        "status": "healthy",
        "service": "Voice2Minutes API",
        "version": "0.1.0"
    }