# main.py
from dotenv import load_dotenv
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions, Microphone
from transcription import TranscriptionHandler
from dialogue_manager import DialogueAggregator

load_dotenv()

def main():
    try:
        # List of languages to process – English is primary.
        languages = ["en-US", "ru"]
        primary_language = "en-US"
        aggregator = DialogueAggregator(expected_languages=languages)
        
        deepgram = DeepgramClient()
        connections = []
        handlers = {}
        
        # Base transcription options for shared settings.
        base_options = {
            "smart_format": True,
            "encoding": "linear16",
            "diarize": True,
            "channels": 1,
            "sample_rate": 16000,
            "interim_results": True,
            "utterance_end_ms": "1000",
            "vad_events": True,
            "endpointing": 300,
            "filler_words": True,
            "intents": True,
        }
        
        addons = {"no_delay": "true"}
        
        # Create a connection and handler for each language.
        for lang in languages:
            # Use nova-3 for English and nova-2 for other languages.
            model = "nova-3" if lang == "en-US" else "nova-2"
            
            options = LiveOptions(
                model=model,
                language=lang,
                smart_format=base_options["smart_format"],
                encoding=base_options["encoding"],
                diarize=base_options["diarize"],
                channels=base_options["channels"],
                sample_rate=base_options["sample_rate"],
                interim_results=base_options["interim_results"],
                utterance_end_ms=base_options["utterance_end_ms"],
                vad_events=base_options["vad_events"],
                endpointing=base_options["endpointing"],
                filler_words=base_options["filler_words"],
                # If Deepgram supports intents as an option:
                # intents=base_options["intents"],
            )
            connection = deepgram.listen.websocket.v("1")
            handler = TranscriptionHandler(language=lang, aggregator=aggregator)
            connection.on(LiveTranscriptionEvents.Open, handler.on_open)
            connection.on(LiveTranscriptionEvents.Transcript, handler.on_message)
            connection.on(LiveTranscriptionEvents.Metadata, handler.on_metadata)
            connection.on(LiveTranscriptionEvents.SpeechStarted, handler.on_speech_started)
            connection.on(LiveTranscriptionEvents.UtteranceEnd, handler.on_utterance_end)
            connection.on(LiveTranscriptionEvents.Close, handler.on_close)
            connection.on(LiveTranscriptionEvents.Error, handler.on_error)
            connection.on(LiveTranscriptionEvents.Unhandled, handler.on_unhandled)
            
            if not connection.start(options, addons=addons):
                print(f"Failed to connect to Deepgram for language {lang}")
                continue
            
            connections.append(connection)
            handlers[lang] = handler
        
        if not connections:
            print("No connections established.")
            return
        
        # Broadcast audio to every connection.
        def broadcast_audio(data):
            for conn in connections:
                conn.send(data)
        
        print("\nPress Enter to stop recording...\n")
        microphone = Microphone(broadcast_audio)
        microphone.start()
        
        input("Press Enter to stop recording...\n")
        
        microphone.finish()
        for conn in connections:
            conn.finish()

        # Optionally, print the aggregated dialogue.
        # print(aggregator.get_aggregated_dialogue())
        
        print("Finished")
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()
