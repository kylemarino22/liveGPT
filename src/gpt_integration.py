# gpt_integration.py
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def stream_gpt4_response(conversation_text: str, handler, request_id: int):
    """
    Streams a GPT‑4 response based on the aggregated dialogue.
    The system prompt instructs GPT‑4 to choose which language to respond in,
    and if it wants to speak, to begin its message with "/say <Language> <text>".
    """
    # Print the full dialogue (including previous Person 1 and GPT responses).
    print("\n[New GPT Call Initiated]")
    print("Full GPT Dialogue:")
    print(conversation_text)
    
    print("\nStreaming GPT‑4 Response:")
    response_text = ""
    partial_word = ""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a conversational partner who is responding to messages in real time."
                        "You are getting a live audio feed of transcribed messages. Some messages may be segmented in multiple lines."
                        "Do not interrupt if someone is speaking; wait until they have fully expressed their idea before responding. "
                        "Chill with the long responses, act like a human."
                        "There are multiple transcriber bots which will provide transcriptions for each speaker in the following format:\n"
                        "[Speaker: N, Language: language1]: ...\n"
                        "[Speaker: N, Language: language2]: ...\n"
                        "If you don't want to say anything, respond with /say Nothing\n"
                        "When you respond, choose one appropriate language to use. Begin your message with /say <Language> followed by your response.\n"
                        "You can think internally before speaking, and if it makes sense to let someone else speak, respond with /pausing\n"
                    )
                },
                {"role": "user", "content": conversation_text}
            ],
            stream=True  # Enable streaming mode.
        )
        for chunk in response:
            if handler.current_gpt_request_id != request_id:
                print("\n[GPT response cancelled due to a new request]\n")
                break
            
            content = chunk.choices[0].delta.content
            if content:
                text = partial_word + content
                if text.endswith(" "):
                    print(text, end="", flush=True)
                    response_text += text
                    partial_word = ""
                else:
                    words = text.split(" ")
                    if len(words) > 1:
                        complete_words = " ".join(words[:-1]) + " "
                        print(complete_words, end="", flush=True)
                        response_text += complete_words
                        partial_word = words[-1]
                    else:
                        partial_word = text
        if partial_word:
            print(partial_word, end="", flush=True)
            response_text += partial_word
        
        print("\n\n--- End of GPT‑4 Response ---\n")
        # If the response wasn't cancelled, add it to the aggregator.
        if handler.current_gpt_request_id == request_id:
            handler.aggregator.add_gpt_response(response_text)
    except Exception as e:
        print(f"Error in GPT‑4 integration: {e}")
