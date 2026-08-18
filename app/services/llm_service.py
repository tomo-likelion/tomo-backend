from openai import OpenAI, OpenAIError

from app.core.config import get_settings
from app.prompts.cultural_prompt import SYSTEM_PROMPT, build_analysis_prompt
from app.schemas.email_analysis import EmailAnalysisCreateRequest, LLMAnalysisResult
from app.schemas.recipient import RecipientProfileResponse
from app.services.risk_scoring import (
    calculate_risk_score,
    normalize_risk_severities,
)


class LLMNotConfiguredError(Exception):
    pass


class LLMAnalysisError(Exception):
    pass


def analyze_email_with_llm(
    request: EmailAnalysisCreateRequest,
    recipient: RecipientProfileResponse,
) -> LLMAnalysisResult:
    settings = get_settings()

    if settings.openai_api_key is None:
        raise LLMNotConfiguredError

    client = OpenAI(api_key=settings.openai_api_key.get_secret_value())

    try:
        response = client.responses.parse(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_analysis_prompt(request, recipient),
                },
            ],
            text_format=LLMAnalysisResult,
        )
    except OpenAIError as error:
        raise LLMAnalysisError from error

    result = response.output_parsed
    if result is None:
        raise LLMAnalysisError

    normalize_risk_severities(result.analysis.risks)
    result.analysis.risk_score = calculate_risk_score(result.analysis.risks)
    return result
