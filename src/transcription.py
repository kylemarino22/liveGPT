# transcription.py
import threading
import time
import uuid
from deepgram import LiveTranscriptionEvents
from gpt_integration import stream_gpt4_response

# Global variables to coordinate GPT call initiation across threads.
gpt_call_lock = threading.Lock()
gpt_call_pending = False

class TranscriptionHandler:
    def __init__(self, language, aggregator):
        self.language = language
        self.aggregator = aggregator
        self.final_chunks = []          # Buffer for final transcript pieces.
        self.current_utterance_id = None  # Unique ID for the current utterance.
        self.current_gpt_request_id = 0

    def on_open(self, *args, **kwargs):
        print(f"[{self.language}] Connection opened.")

    def on_message(self, *args, **kwargs):
        result = kwargs.get("result", args[0] if args else None)
        if not result:
            return

        transcript = result.channel.alternatives[0].transcript
        if not transcript:
            return

        # print(result)

        # Check if there are word-level details (diarization info).
        words = result.channel.alternatives[0].words
        if not words:
            speaker = "Unknown"
            print(f"[{self.language}] {speaker}: {transcript}")
            return

        if result.is_final:
            # Build a readable, diarized transcript.
            current_speaker = None
            current_line = ""
            speaker_lines = []
            for word in words:
                # Each word object is assumed to have a 'word' attribute and a 'speaker' attribute.
                speaker = getattr(word, 'speaker', 'Unknown')
                if current_speaker is None:
                    current_speaker = speaker
                if speaker != current_speaker:
                    speaker_lines.append(f"[Speaker: {current_speaker}, Language: {self.language}]: {current_line.strip()}")
                    current_line = word.word + " "
                    current_speaker = speaker
                else:
                    current_line += word.word + " "
            if current_line:
                speaker_lines.append(f"[Speaker: {current_speaker}, Language: {self.language}]: {current_line.strip()}")

            # Update aggregator with the final transcript.
            # self.final_chunks.(transcript)
            for line in speaker_lines:
                self.aggregator.append_speaker_entry(line)

            # if not self.current_utterance_id:
            #     self.current_utterance_id = str(uuid.uuid4())
            # utterance_text = " ".join(self.final_chunks)
            # self.aggregator.update_transcription(
            #     self.current_utterance_id, 
            #     self.language, 
            #     utterance_text, 
            #     finalize=True
            # )
            self.maybe_initiate_gpt_call()
            # self.final_chunks = []
        else:
            # For interim results, you can choose to print or ignore.
            pass

    def maybe_initiate_gpt_call(self):
        global gpt_call_pending
        with gpt_call_lock:
            if not gpt_call_pending:
                gpt_call_pending = True
                threading.Timer(0.2, self.trigger_gpt_call).start()

    def trigger_gpt_call(self):
        global gpt_call_pending
        conversation_text = self.aggregator.get_aggregated_dialogue()
        self.current_gpt_request_id += 1
        current_request = self.current_gpt_request_id
        stream_gpt4_response(conversation_text, self, current_request)
        with gpt_call_lock:
            gpt_call_pending = False

    def on_close(self, *args, **kwargs):
        print(f"[{self.language}] Connection closed.")

    def on_error(self, *args, **kwargs):
        error = kwargs.get("error", args[0] if args else None)
        print(f"[{self.language}] Error: {error}")

    def on_unhandled(self, *args, **kwargs):
        pass

    def on_metadata(self, *args, **kwargs):
        pass

    def on_speech_started(self, *args, **kwargs):
        pass

    def on_utterance_end(self, *args, **kwargs):
        pass
