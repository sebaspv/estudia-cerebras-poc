from pydantic import BaseModel


class Subject(BaseModel):
    _primary_key_field: str = "id"
    class_name: str
    latest_reading: str
    latest_exam: str
    latest_answers: str
