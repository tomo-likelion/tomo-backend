from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Relationship(str, Enum):
    PARTNER = "PARTNER"
    CLIENT = "CLIENT"
    COWORKER = "COWORKER"


class RecipientProfileResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: int
    email: EmailStr
    name: str
    country_code: str = Field(alias="countryCode", min_length=2, max_length=2)
    language_code: str = Field(alias="languageCode", min_length=2, max_length=5)
    relationship: Relationship
    organization: str


class RecipientNotFoundResponse(BaseModel):
    code: str = "RECIPIENT_NOT_FOUND"
    message: str = "등록되지 않은 수신자입니다."
