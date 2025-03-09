# main.py
from dotenv import load_dotenv
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions, Microphone
from transcription import TranscriptionHandler

load_dotenv()

def main():
    try:
        # Create a Deepgram client with default configuration.
        deepgram = DeepgramClient()
        dg_connection = deepgram.listen.websocket.v("1")

        # Instantiate our transcription handler.
        handler = TranscriptionHandler()

        # Register event handlers from the transcription handler.
        dg_connection.on(LiveTranscriptionEvents.Open, handler.on_open)
        dg_connection.on(LiveTranscriptionEvents.Transcript, handler.on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, handler.on_metadata)
        dg_connection.on(LiveTranscriptionEvents.SpeechStarted, handler.on_speech_started)
        dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, handler.on_utterance_end)
        dg_connection.on(LiveTranscriptionEvents.Close, handler.on_close)
        dg_connection.on(LiveTranscriptionEvents.Error, handler.on_error)
        dg_connection.on(LiveTranscriptionEvents.Unhandled, handler.on_unhandled)

        # Configure live transcription options.
        options = LiveOptions(
            model="nova-3",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            diarize=True,
            channels=1,
            sample_rate=16000,
            interim_results=True,
            utterance_end_ms="1000",
            vad_events=True,
            endpointing=300,
        )

        addons = {"no_delay": "true"}

        print("\nPress Enter to stop recording...\n")
        if not dg_connection.start(options, addons=addons):
            print("Failed to connect to Deepgram")
            return

        # Open a microphone stream on the default input device.
        microphone = Microphone(dg_connection.send)
        microphone.start()

        input("Press Enter to stop recording...\n")

        # Stop the microphone and Deepgram connection.
        microphone.finish()
        dg_connection.finish()

        print("Finished")
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()
