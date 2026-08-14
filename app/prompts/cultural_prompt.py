from app.schemas.email_analysis import EmailAnalysisCreateRequest
from app.schemas.recipient import RecipientProfileResponse


SYSTEM_PROMPT = """
You are TOMO, an expert in cross-cultural business email communication.

Analyze the draft using the recipient's country, language, and business
relationship. Focus on expressions that may be interpreted as personal blame,
face-threatening feedback, excessive directness, coercive commands, or a tone
that does not fit the relationship.

Preserve the sender's intent. Explain risks as possibilities rather than facts,
and do not stereotype everyone from a country. Rewrite the email in the
recipient's language with a natural business tone appropriate to the stated
relationship. The recommendation must keep the original request while reducing
avoidable cultural misunderstanding.
""".strip()


def build_analysis_prompt(
    request: EmailAnalysisCreateRequest,
    recipient: RecipientProfileResponse,
) -> str:
    return f"""
Recipient context:
- Name: {recipient.name}
- Country code: {recipient.country_code}
- Language code: {recipient.language_code}
- Relationship: {recipient.relationship.value}
- Organization: {recipient.organization}

Draft email:
- Subject: {request.subject}
- Body: {request.body}

Identify the sender's intent and request. Detect culturally sensitive wording,
including direct criticism that may threaten the recipient's face and commands
that may be too forceful for an external business relationship. For each risk,
quote the relevant text, explain the possible interpretation, and suggest a
safer alternative. Then produce a localized subject and body.
""".strip()
