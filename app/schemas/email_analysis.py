from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.recipient import Relationship


class EmailIntent(str, Enum):
    REVISION_REQUEST = "REVISION_REQUEST"
    INFORMATION_REQUEST = "INFORMATION_REQUEST"
    SCHEDULE_CHANGE = "SCHEDULE_CHANGE"
    FEEDBACK = "FEEDBACK"
    APPROVAL_REQUEST = "APPROVAL_REQUEST"
    REJECTION = "REJECTION"
    OTHER = "OTHER"


class RiskType(str, Enum):
    FACE_THREATENING_FEEDBACK = "FACE_THREATENING_FEEDBACK"
    DIRECT_COMMAND = "DIRECT_COMMAND"
    AMBIGUOUS_DEADLINE = "AMBIGUOUS_DEADLINE"
    CULTURAL_TONE = "CULTURAL_TONE"
    RELATIONSHIP_MISMATCH = "RELATIONSHIP_MISMATCH"
    OTHER = "OTHER"


class RiskSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class EmailAnalysisCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    recipient_email: EmailStr = Field(alias="recipientEmail")
    subject: str
    body: str = Field(min_length=1)


class CulturalRisk(BaseModel):
    text: str
    type: RiskType
    severity: RiskSeverity
    reason: str
    suggestion: str


class AnalysisResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    intent: EmailIntent
    request_summary: str = Field(alias="requestSummary")
    risk_score: int = Field(alias="riskScore", ge=0, le=100)
    risks: list[CulturalRisk]


class EmailRecommendation(BaseModel):
    subject: str
    body: str


class LLMAnalysisResult(BaseModel):
    analysis: AnalysisResult
    recommendation: EmailRecommendation


class AnalysisRecipient(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    email: EmailStr
    name: str
    country_code: str = Field(alias="countryCode")
    language_code: str = Field(alias="languageCode")
    relationship: Relationship
    organization: str


class EmailAnalysisCreateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    analysis_id: int = Field(alias="analysisId")
    recipient: AnalysisRecipient
    analysis: AnalysisResult
    recommendation: EmailRecommendation
    created_at: datetime = Field(alias="createdAt")


class EmailAnalysisFailedResponse(BaseModel):
    code: str = "EMAIL_ANALYSIS_FAILED"
    message: str = "이메일 분석에 실패했습니다."


class LLMNotConfiguredResponse(BaseModel):
    code: str = "LLM_NOT_CONFIGURED"
    message: str = "LLM API 설정이 필요합니다."
