from dotenv import load_dotenv
from time import sleep
import logging

from deepgram.utils import verboselogs

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

load_dotenv()

# Global variables for buffering transcript data
is_finals = []
conversation_buffer = []  # This buffer will hold the final transcribed conversation

def main():
    try:
        # Create a Deepgram client (using default config)
        deepgram = DeepgramClient()

        dg_connection = deepgram.listen.websocket.v("1")

        def on_open(self, open, **kwargs):
            print("Connection Open")

        def on_message(self, result, **kwargs):
            global is_finals, conversation_buffer
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            if result.is_final:
                # print(f"Message: {result.to_json()}")
                # Collect final results
                is_finals.append(sentence)

                # When speech_final is True, we've reached an endpoint
                if result.speech_final:
                    utterance = " ".join(is_finals)
                    print(f"Speech Final: {utterance}")
                    conversation_buffer.append(utterance)  # Append the final utterance to the conversation buffer
                    is_finals = []
                else:
                    # Interim final message before speech_final
                    print(f"Is Final: {sentence}")
            else:
                # Interim results for real-time captioning
                print(f"Interim Results: {sentence}")

        def on_metadata(self, metadata, **kwargs):
            # print(f"Metadata: {metadata}")
            pass

        def on_speech_started(self, speech_started, **kwargs):
            print("Speech Started")

        def on_utterance_end(self, utterance_end, **kwargs):
            print("Utterance End")
            global is_finals, conversation_buffer
            if len(is_finals) > 0:
                utterance = " ".join(is_finals)
                # print(f"Utterance End: {utterance}")
                conversation_buffer.append(utterance)  # Append any remaining utterance to the buffer
                is_finals = []

        def on_close(self, close, **kwargs):
            print("Connection Closed")

        def on_error(self, error, **kwargs):
            print(f"Handled Error: {error}")

        def on_unhandled(self, unhandled, **kwargs):
            print(f"Unhandled Websocket Message: {unhandled}")

        # Register event handlers
        dg_connection.on(LiveTranscriptionEvents.Open, on_open)
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
        dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Unhandled, on_unhandled)

        options = LiveOptions(
            model="nova-3",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            interim_results=True,
            utterance_end_ms="1000",
            vad_events=True,
            endpointing=300,
        )

        addons = {
            "no_delay": "true"
        }

        print("\n\nPress Enter to stop recording...\n\n")
        if dg_connection.start(options, addons=addons) is False:
            print("Failed to connect to Deepgram")
            return

        # Open a microphone stream on the default input device
        print("Initializing microphone...")
        microphone = Microphone(dg_connection.send)
        print("Starting microphone...")
        microphone.start()

        # Wait until user input stops the recording
        input("Press Enter to stop recording...\n")

        # Close the microphone and Deepgram connection
        microphone.finish()
        dg_connection.finish()

        print("Finished\n")
        print("Full Conversation:")
        for utterance in conversation_buffer:
            print(utterance)

    except Exception as e:
        print(f"Could not open socket: {e}")
        return

if __name__ == "__main__":
    main()
