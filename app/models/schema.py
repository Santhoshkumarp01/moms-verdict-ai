from pydantic import BaseModel, Field
from typing import List


class VerdictResponse(BaseModel):
    """Structured verdict output for product reviews."""

    summary_en: str = Field(..., description="Summary in English")
    summary_ar: str = Field(..., description="Summary in Arabic")
    pros: List[str] = Field(..., description="List of positive points")
    cons: List[str] = Field(..., description="List of negative points")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment from -1 (negative) to 1 (positive)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the verdict (0 to 1)")
    uncertainty_reason: str = Field(..., description="Reason for uncertainty, or empty string if confident")


class AnalyzeRequest(BaseModel):
    """Input payload for the /analyze endpoint."""

    reviews: List[str] = Field(..., min_length=1, description="List of product review texts")
