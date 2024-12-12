import uvicorn
from dotenv import dotenv_values
from fastapi import FastAPI, Form
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()
DOTENV = dotenv_values(dotenv_path=".env")
TWILIO_ACCOUNT_SID = DOTENV["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = DOTENV["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = DOTENV["TWILIO_PHONE_NUMBER"]

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


@app.post("/webhook/estudia")
async def handle_sms(
    From: str = Form(...),  # Sender's phone number
    To: str = Form(...),  # Receiver's phone number (your Twilio number)
    Body: str = Form(...),  # Message content
):
    response = MessagingResponse()
    response.message("Hello!")
    return str(response)


if __name__ == "__main__":
    uvicorn.run(app)
