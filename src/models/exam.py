from typing import List

from pydantic import BaseModel, Field

from .questions import MCQuestion


class Exam(BaseModel):
    mc_questions: List[MCQuestion] = Field(
        "A list of multiple-choice questions based on the exam topic",
        max_length=3,
        min_length=3,
    )
