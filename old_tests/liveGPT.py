import asyncio
import websockets
import json
import sounddevice as sd
import openai
import time
import pyttsx3

# API Keys
DEEPGRAM_API_KEY = "deekpgram-api-key"
OPENAI_API_KEY = "openai-api-key"

# GPT-4 System Instruction
GPT_INSTRUCTION = """You are an AI participant in a conversation, responding only when necessary. You can speak both English and Russian. Follow these rules:
- Respond **only if relevant**.
- **Always respond if someone refers to you as 'GPT'**.
- **Use the appropriate language (English or Russian) depending on context**.
- If asked to translate, **always use the target language**.
- Use the format: **/say "your response"** when responding.
- Otherwise, remain silent.
"""

# Deepgram WebSocket URL (English + Russian with speaker diarization)
DEEPGRAM_WS_URL = f"wss://api.deepgram.com/v1/listen?access_token=2be0c34a27d784de8482d82680cb6f7007f05214&language=en&alternative_languages=ru&diarization=true"

# Global variables for tracking conversation
last_speech_time = time.time()
conversation_history = []
tts_engine = pyttsx3.init()  # Text-to-Speech Engine


async def transcribe_live():
    """Handles real-time transcription and triggers GPT-4 when necessary."""
    global last_speech_time, conversation_history

    async with websockets.connect(DEEPGRAM_WS_URL) as ws:

        def audio_callback(indata, frames, time, status):
            """Captures live audio and streams it to Deepgram."""
            if status:
                print(status)
            ws.send(indata.tobytes())

        # Open microphone stream
        with sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=audio_callback):
            print("🎤 Listening... Speak in English or Russian (Ctrl+C to stop)")

            async for message in ws:
                data = json.loads(message)

                if "channel" in data:
                    transcript = data["channel"]["alternatives"][0]["transcript"]
                    speakers = data["metadata"]["channels"][0]["diarization"]

                    if transcript:
                        print(f"🗣 {speakers}: {transcript}")
                        conversation_history.append(f"{speakers}: {transcript}")
                        last_speech_time = time.time()

                        # # If GPT is mentioned, trigger an immediate response
                        # if "GPT" in transcript.upper():
                        #     await process_with_gpt4(force_response=True)

                # If 2 seconds of silence, send conversation to GPT-4
                if time.time() - last_speech_time > 2:
                    await process_with_gpt4()


async def process_with_gpt4(force_response=False):
    """Sends conversation history to GPT-4 and processes its response."""
    global conversation_history

    # Prepare messages for GPT-4
    messages = [{"role": "system", "content": GPT_INSTRUCTION}]
    for line in conversation_history[-10:]:  # Send last 10 exchanges
        messages.append({"role": "user", "content": line})

    # Call GPT-4 API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY
    )

    # Extract response
    gpt_response = response["choices"][0]["message"]["content"].strip()

    # GPT-4 decides to respond only when necessary
    if gpt_response.startswith("/say ") or force_response:
        print(f"🤖 AI: {gpt_response}")

        # Convert response to speech
        await text_to_speech(gpt_response[6:-1])  # Remove /say "quotes"

    # Clear conversation history after processing
    conversation_history = []


async def text_to_speech(text):
    """Converts AI text response into speech using a TTS engine."""
    print(f"🔊 AI is speaking: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()


# Run live transcription
asyncio.run(transcribe_live())
