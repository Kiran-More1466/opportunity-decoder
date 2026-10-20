from fastapi import APIRouter, HTTPException

from .schemas import AnalysisReport, AnalyzeRequest
from .services.errors import AnalysisError
from .services.gemini import analyze_with_gemini

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/api/analyze", response_model=AnalysisReport)
async def analyze(request: AnalyzeRequest) -> AnalysisReport:
    try:
        return await analyze_with_gemini(request)
    except AnalysisError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
