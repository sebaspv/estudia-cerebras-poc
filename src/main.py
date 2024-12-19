import json

import redis
import uvicorn
from dotenv import dotenv_values
from fastapi import FastAPI, Form, Response
from langchain_cerebras import ChatCerebras
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from helpers.genshortid import short_uuid
from models.exam import Exam
from models.reading import Reading
from models.subject import Subject

app = FastAPI()
DOTENV = dotenv_values(dotenv_path=".env")
TWILIO_ACCOUNT_SID = DOTENV["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = DOTENV["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = DOTENV["TWILIO_PHONE_NUMBER"]
REDIS_HOST = DOTENV["REDIS_URL"]
REDIS_PASSWORD = DOTENV["REDIS_PASSWORD"]

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
model = ChatCerebras(model="llama-3.3-70b", temperature=0.2, top_p=0.9)
exam_model = model.with_structured_output(Exam)
reading_model = model.with_structured_output(Reading)
r = redis.Redis(
    host=REDIS_HOST,
    port=18201,
    decode_responses=True,
    password=REDIS_PASSWORD,
)


@app.post("/webhook/estudia")
async def handle_sms(
    From: str = Form(...),  # Sender's phone number
    To: str = Form(...),  # Receiver's phone number (your Twilio number)
    Body: str = Form(...),  # Message content
):
    msg = Body
    response = MessagingResponse()
    split_msg = msg.split()
    if split_msg[0] == "teacher":
        name = split_msg[1]
        init_topic = " ".join(split_msg[2:])
        id = short_uuid()
        student_id = short_uuid()
        new_class = Subject(
            class_name=name,
            latest_reading=reading_model.invoke(
                f"Generate study material on the topic of {init_topic}. Make it a paragraph long."
            ),
            latest_exam=exam_model.invoke(f"Generate a school exam about {init_topic}"),
            student_id=student_id,
        )
        r.set(id, json.dumps(new_class.model_dump()))
        r.set(student_id, id)
        response.message(
            f"Class created successfully with your ID {id} :). Share this code with your students: {student_id}\n\n"
        )
    else:
        # TODO: actually parse the exam
        parsed_id = split_msg[0]
        option = split_msg[1]
        if option == "exam":
            data = json.loads(r.get(r.get(parsed_id)))  # parsed id is from student
            questions = data["latest_exam"]["mc_questions"]
            parsed_questions = []
            for question in questions:
                parsed_questions.append(
                    (question["question"], question["answers"])
                )  # tuple of (str, list[str])
            final_message = "Please answer the following:\n\n"
            for question, answers in parsed_questions:
                final_message += question + "\n"
                option_index = 1
                for answer in answers:
                    final_message += str(option_index) + ". " + answer + "\n"
                    option_index += 1
            response.message(final_message)

        elif option == "change":
            new_topic = " ".join(split_msg[2:])
            cur_data = json.loads(
                r.get(parsed_id)
            )  # SHOULD BE A SINGLE PARSE: only teachers can access this feature (obviously)
            cur_data["latest_exam"] = exam_model.invoke(
                f"Generate a school exam about {new_topic}"
            ).model_dump()
            cur_data["latest_reading"] = reading_model.invoke(
                f"Generate study material on the topic of {new_topic}. Make it a paragraph long."
            ).model_dump()
            r.set(parsed_id, json.dumps(cur_data))

        elif option == "reading":
            data = json.loads(r.get(r.get(parsed_id)))
            response.message(
                str(data["latest_reading"]["topic"])
                + "\n"
                + str(data["latest_reading"]["content"])
            )

        elif option == "answer":
            data = json.loads(r.get(r.get(parsed_id)))
            questions = data["latest_exam"]["mc_questions"]
            grade = 0
            for question, user_answer in zip(questions, split_msg[2:]):
                if question["answer"] == int(user_answer) - 1:
                    grade += 1
            percentage_grade = round((grade / len(questions)) * 100)
            response.message(
                f"Okay! You got a {percentage_grade}% in this exam. Good job :)\n\n"
            )

    return Response(content=str(response), media_type="application/xml")


@app.get("/get-exam")
async def get_exam(student_id: str) -> dict:
    if r.exists(student_id):
        return json.loads(r.get(r.get(student_id)))
    return {"message": "class not found"}


@app.get("/get-reading")
async def get_reading(student_id: str) -> dict:
    if r.exists(student_id):
        return json.loads(
            r.get(r.get(student_id))
        )  # looks ugly, but at least students have different IDs than teachers
    return {"message": "class not found"}


@app.post("/add-topic")
async def add_topic(id: str, topic: str):
    if r.exists(id):
        pass
    return {"message": "class not found"}


@app.post("/create-class")
async def create_class(name: str, initial_topic: str) -> dict:
    id = short_uuid()
    student_id = short_uuid()
    new_class = Subject(
        class_name=name,
        latest_reading=reading_model.invoke(
            f"Generate study material on the topic of {initial_topic}. Make it a paragraph long."
        ),
        latest_exam=exam_model.invoke(f"Generate a school exam about {initial_topic}"),
        student_id=student_id,
    )
    r.set(id, json.dumps(new_class.model_dump()))
    r.set(student_id, id)
    return {"class_id": id}


if __name__ == "__main__":
    uvicorn.run(app)
