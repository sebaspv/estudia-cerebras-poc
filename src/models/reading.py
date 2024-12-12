from pydantic import BaseModel, Field


class Reading(BaseModel):
    topic: str = Field(description="The title of the reading material")
    content: str = Field(
        description="Short-form reading material for studying purposes", max_length=1000
    )
