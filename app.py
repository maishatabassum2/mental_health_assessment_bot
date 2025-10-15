from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from phq9_session import PHQ9Session  # Your PHQ-9 session manager
from google.cloud import texttospeech
from io import BytesIO
import os
import base64
from langdetect import detect  # For language detection in TTS


load_dotenv()

app = FastAPI()


client = OpenAI()

# CORS(eita connection of two ports lalalal)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# static files ashe ekhane.
app.mount("/static", StaticFiles(directory="static"), name="static")


phq9_session = PHQ9Session()


# JSON path
GOOGLE_TTS_JSON = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "/Users/nishat/Downloads/maisha give bangla/final_project/mental_health_project/google_bangla_TTS.json"
)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_TTS_JSON


class UserInput(BaseModel):
    user_response: str


@app.get("/")
async def root():
    return FileResponse("static/upload.html")

#Transcription endpoint eitaaaa
@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=(file.filename, file.file, file.content_type)
        )
        return {"transcript": result.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# LLM response 
def detect_and_respond(text: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a friendly mental health assistant. "
                "If the user seems sad, anxious, or overwhelmed, gently guide them through a PHQ-9 assessment. "
                "Otherwise, chat naturally like a supportive friend."
            )
        },
        {"role": "user", "content": text}
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return response.choices[0].message.content

# Google TTS function 
def synthesize_speech_bytes(text: str) -> BytesIO:
    tts_client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)

    try:
        lang_detected = detect(text)
    except:
        lang_detected = "en"

    lang_code = "bn-BD" if lang_detected.startswith("bn") else "en-US"

    voice = texttospeech.VoiceSelectionParams(
        language_code=lang_code,
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = tts_client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    return BytesIO(response.audio_content)

# TTS endpoint 
@app.post("/tts")
async def tts_endpoint(input: UserInput):
    audio_bytes = synthesize_speech_bytes(input.user_response.strip())
    audio_bytes.seek(0)
    audio_b64 = base64.b64encode(audio_bytes.read()).decode("utf-8")
    return JSONResponse(content={"audio_base64": audio_b64})

#  PHQ-9 endpoint 
@app.post("/phq")
async def phq(input: UserInput):
    user_text = input.user_response.strip()

    if user_text.lower() == "start" or phq9_session.started:
        result = phq9_session.process_response(user_text)
        return {"response": result["bot_message"], "interrupted": result.get("interrupted", False)}

    reply = detect_and_respond(user_text)

    if any(phrase in reply for phrase in ["PHQ-9", "Would you like to", "start a quick screening"]):
        intro = (
            "Of course, I'm here to help. The PHQ-9 assessment can help us understand how you’ve been feeling. "
            "You can take your time with each response."
        )
        start_msg = phq9_session.start()["bot_message"]
        full_msg = f"{intro}\n\n{start_msg}"
        return {"response": full_msg, "interrupted": False}

    return {"response": reply, "interrupted": False}

#  PHQ-9 reset 
@app.post("/phq/reset")
async def phq_reset():
    phq9_session.reset()
    return {"status": "reset"}
