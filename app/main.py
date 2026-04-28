from fastapi import FastAPI, HTTPException
from app.models.schema import AnalyzeRequest, VerdictResponse
from app.services.processing import analyze_reviews
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Mom's Verdict AI",
    description="AI-powered product review analyzer with structured verdicts",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=VerdictResponse)
def analyze(request: AnalyzeRequest):
    """Analyze a list of product reviews and return a structured verdict.

    Args:
        request: AnalyzeRequest containing a list of review strings.

    Returns:
        VerdictResponse with summary, pros, cons, sentiment, confidence, and uncertainty.
    """
    non_empty = [r.strip() for r in request.reviews if r.strip()]
    if not non_empty:
        raise HTTPException(status_code=422, detail="All reviews are empty or whitespace.")

    try:
        result = analyze_reviews(non_empty)
        return result
    except RuntimeError as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
