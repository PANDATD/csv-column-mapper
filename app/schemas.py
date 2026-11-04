"""Request and response schemas."""
from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    source_columns: list[str] = Field(min_length=1, max_length=500)
    destination_columns: list[str] = Field(min_length=1, max_length=500)
    mappings: dict[str, str] = Field(default_factory=dict)


class ReviewResponse(BaseModel):
    mappings: dict[str, str]
    count: int
