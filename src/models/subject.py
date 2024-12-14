from pydantic import BaseModel

from .exam import Exam
from .reading import Reading


class Subject(BaseModel):
    student_id: str
    class_name: str
    latest_reading: Reading
    latest_exam: Exam
