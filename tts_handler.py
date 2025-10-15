import io
from google.cloud import texttospeech

# Path to your service account JSON
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_bangla_TTS.json"

def bangla_tts_bytes(text: str) -> bytes:
    """
    Convert Bangla text to speech using Google Cloud TTS.
    Returns MP3 audio as bytes (in-memory).
    """
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="bn-IN",
        name="bn-IN-Standard-A"
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,
        pitch=0
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    return response.audio_content  # bytes
