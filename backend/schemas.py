from typing import List

from pydantic import (
    BaseModel,
    Field,
    field_validator
)


class DocumentRequest(BaseModel):

    document_type: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=4000
    )

    terms: List[str] = Field(
        ...,
        min_length=1,
        max_length=50
    )

    effective_date: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    jurisdiction: str = Field(
        default="Not specified",
        max_length=200
    )

    additional_instructions: str = Field(
        default="",
        max_length=5000
    )


    @field_validator("terms")
    @classmethod
    def clean_terms(cls, value):

        cleaned = [
            item.strip()
            for item in value
            if item and item.strip()
        ]

        if not cleaned:
            raise ValueError(
                "At least one term is required."
            )

        return cleaned


class DocumentResponse(BaseModel):

    document_type: str

    title: str

    content: str

    terms: List[str]

    disclaimer: str
