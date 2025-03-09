# dialogue_manager.py
import threading
import os
import json

class DialogueAggregator:
    def __init__(self, expected_languages, filename="dialogue_entries.json"):
        self.expected_languages = expected_languages
        self.filename = filename
        self.lock = threading.Lock()
        self.entries = []
        self._load_entries()

    def _load_entries(self):
        """Load dialogue entries from file if it exists."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
                print(f"Loaded {len(self.entries)} entries from {self.filename}")
            except Exception as e:
                print(f"Error loading dialogue entries: {e}")

    def _save_entries(self):
        """Persist dialogue entries to file."""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving dialogue entries: {e}")

    def append_speaker_entry(self, entry):
        with self.lock:
            self.entries.append(entry)
            self._save_entries()

    def add_gpt_response(self, response_text):
        with self.lock:
            self.entries.append(f"[Speaker: GPT] {response_text}")
            self._save_entries()

    def is_entry_complete(self, utterance_id):
        with self.lock:
            if not self.entries or not isinstance(self.entries[-1], dict) or self.entries[-1].get("utterance_id") != utterance_id:
                return False
            entry = self.entries[-1]
            for lang in self.expected_languages:
                if lang not in entry.get("transcriptions", {}):
                    return False
            return True

    def get_aggregated_dialogue(self):
        with self.lock:
            # If entries are stored as dicts then you'll need to format them;
            # here we assume entries are simple strings.
            return "\n".join(self.entries)
