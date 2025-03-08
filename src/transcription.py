# transcription.py
import threading
from deepgram import LiveTranscriptionEvents
from gpt_integration import stream_gpt4_response

class TranscriptionHandler:
    def __init__(self):
        self.is_finals = []            # Temporary buffer for final chunks
        self.dialogue = []             # Full conversation dialogue (User and GPT)
        self.current_gpt_request_id = 0  # New attribute to track the active GPT request

    def on_open(self, *args, **kwargs):
        pass

    def on_message(self, *args, **kwargs):
        result = kwargs.get("result", args[0] if args else None)
        if not result:
            return

        sentence = result.channel.alternatives[0].transcript
        if not sentence:
            return

        if result.is_final:
            self.is_finals.append(sentence)
            if result.speech_final:
                # Final utterance completed.
                utterance = " ".join(self.is_finals)
                print(f"\nFinal Transcribed Audio: {utterance}\n")
                # Append the user utterance to the dialogue.
                self.dialogue.append("User: " + utterance)
                self.is_finals = []
                # Prepare the full dialogue so far to send to GPT.
                conversation_text = "\n".join(self.dialogue)
                # Increment the GPT request id so that any previous streaming is cancelled.
                self.current_gpt_request_id += 1
                current_request = self.current_gpt_request_id
                # Call GPT‑4 in a separate thread, passing the current request id.
                thread = threading.Thread(target=stream_gpt4_response, args=(conversation_text, self, current_request))
                thread.start()
            else:
                # For a final chunk that isn’t a full utterance yet.
                print(f"Final Chunk: {sentence}")
        else:
            print(f"Current Transcribed Audio: {sentence}")

    def on_metadata(self, *args, **kwargs):
        pass

    def on_speech_started(self, *args, **kwargs):
        pass

    def on_utterance_end(self, *args, **kwargs):
        if self.is_finals:
            utterance = " ".join(self.is_finals)
            print(f"\nFinal Transcribed Audio (Utterance End): {utterance}\n")
            self.dialogue.append("User: " + utterance)
            self.is_finals = []

    def on_close(self, *args, **kwargs):
        pass

    def on_error(self, *args, **kwargs):
        error = kwargs.get("error", args[0] if args else None)
        print(f"Error: {error}")

    def on_unhandled(self, *args, **kwargs):
        pass
