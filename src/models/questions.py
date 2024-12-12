from typing import List

from pydantic import BaseModel, Field


class MCQuestion(BaseModel):
    question: str = Field(
        description="A multiple choice exam-type question based on the concept, only one option is correct"
    )
    answers: List[str] = Field(
        description="The answer options", min_length=4, max_length=4
    )
    answer: int = Field(description="The correct answer index", ge=0, le=3)


class TFQuestion(BaseModel):
    question: str = Field(
        description="A true or false exam-type question based on the concept. Structure it as a question."
    )
    answer: bool = Field(description="The answer to the question")
