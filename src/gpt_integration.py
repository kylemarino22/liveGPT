# gpt_integration.py
import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def stream_gpt4_response(conversation_text: str, handler, request_id: int):
    """
    Streams a GPT‑4 response based on the full dialogue.
    As new data arrives, it updates the corresponding GPT response entry in the dialogue.
    If a new request interrupts this stream, the partial response remains and the new utterance is appended afterward.
    """
    print("\nStreaming GPT‑4 Response:")
    response_text = ""
    partial_word = ""
    # Create a new dialogue entry for the GPT response and record its index.
    handler.dialogue.append("GPT: ")
    gpt_index = len(handler.dialogue) - 1

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": conversation_text}],
            stream=True  # Enable streaming mode
        )
        for chunk in response:
            # Check if a new GPT request has been triggered.
            if handler.current_gpt_request_id != request_id:
                print("\n[GPT response cancelled due to a new request]\n")
                break  # Exit the loop early if a new request has started.
            
            content = chunk.choices[0].delta.content
            if content:
                text = partial_word + content
                if text.endswith(" "):
                    words = text.split()
                    for word in words:
                        print(word, end=" ", flush=True)
                    response_text += text
                    partial_word = ""
                else:
                    words = text.split(" ")
                    if len(words) > 1:
                        complete_words = words[:-1]
                        for word in complete_words:
                            print(word, end=" ", flush=True)
                        response_text += " ".join(complete_words) + " "
                        partial_word = words[-1]
                    else:
                        partial_word = text
                # Update the dialogue entry in real time.
                handler.dialogue[gpt_index] = "GPT: " + response_text + partial_word
        
        # After streaming completes, check if any word fragment remains.
        if partial_word:
            print(partial_word, end=" ", flush=True)
            response_text += partial_word
        
        print("\n\n--- End of GPT‑4 Response ---\n")
        
        # Finalize the dialogue entry.
        if handler.current_gpt_request_id == request_id:
            handler.dialogue[gpt_index] = "GPT: " + response_text
        else:
            # Optionally, note that this GPT response was partial.
            handler.dialogue[gpt_index] = "GPT (partial, cancelled): " + response_text

        full_dialogue = "\n".join(handler.dialogue)
        print("Full Dialogue Up Until Now:\n" + full_dialogue + "\n")
    except Exception as e:
        print(f"Error in GPT‑4 integration: {e}")
