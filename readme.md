# Live Transcription & GPT Integration

This project streams live audio from your microphone to Deepgram for transcription and then sends the transcribed dialogue to GPT‑4 for a real-time response. The GPT‑4 response is updated live as data comes in, and if a new request is triggered, the interruption is added after the current response.

Note: This readme is mostly AI generated, so it may contain mistakes.

## Features

- **Live Transcription:** Uses Deepgram's WebSocket API to stream and transcribe audio.
- **Real-Time GPT‑4 Streaming:** Streams GPT‑4 responses word-by-word and updates the dialogue in real time.
- **Interruption Handling:** If a new GPT‑4 request is triggered, the current partial response remains in the dialogue and is marked as partial.

## Prerequisites

- **Python 3.10** (or later, but this guide assumes Python 3.10)
- A Deepgram API key (if required by your Deepgram account)
- An OpenAI API key with access to GPT‑4
- Conda (if you prefer managing your environments with Conda)

## Installation

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Create a Conda Environment with Python 3.10

If you use Conda, create and activate a new environment:

```bash
conda create -n live_transcription_env python=3.10
conda activate live_transcription_env
```

### 3. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

## Setup

### 1. Export Your API Keys

You need to provide your Deepgram and OpenAI API keys as environment variables. There are two common approaches:

#### Option A: Using a `.env` File

Create a file named `.env` in the project root directory and add:

```env
OPENAI_API_KEY=your_openai_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
```

Ensure you have the `python-dotenv` package installed (it's listed in `requirements.txt`), so these keys are automatically loaded when you run the project.

#### Option B: Exporting Environment Variables Directly

Alternatively, you can export the variables in your terminal session before running the project:

On Unix or macOS:

```bash
export OPENAI_API_KEY=your_openai_api_key_here
export DEEPGRAM_API_KEY=your_deepgram_api_key_here
```

On Windows (Command Prompt):
NOTE: I only test on mac, so windows may have some issues.

```batch
set OPENAI_API_KEY=your_openai_api_key_here
set DEEPGRAM_API_KEY=your_deepgram_api_key_here
```

On Windows (PowerShell):

```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
$env:DEEPGRAM_API_KEY="your_deepgram_api_key_here"
```

### 2. Configure Your Microphone

Ensure your microphone is configured and accessible on your system as the project streams live audio.

## Running the Project

Simply run the main script:

```bash
python main.py
```

You will see prompts to start and stop recording. The application will stream audio to Deepgram, process the transcription, and then send completed utterances to GPT‑4 for real-time responses.

## Project Structure

- **main.py:** Initializes the Deepgram client, starts the microphone stream, and ties together transcription and GPT‑4 integration.
- **transcription.py:** Contains the `TranscriptionHandler` class, which manages Deepgram events and processes the transcription.
- **gpt_integration.py:** Handles streaming of the GPT‑4 response and updates the dialogue buffer in real time.

## Customization

- **Deepgram Options:** Modify the settings in `LiveOptions` (e.g., model, language, encoding) in `main.py` to fit your needs.
- **Response Handling:** Update the logic in `TranscriptionHandler` or `stream_gpt4_response` in `gpt_integration.py` if you need custom interruption or response handling.

## Troubleshooting

- **API Keys:** Ensure that your API keys are correctly set in the `.env` file or exported in your terminal session.
- **Microphone Access:** Confirm that your microphone is set as the default input device and is accessible.
- **Internet Connection:** Both Deepgram and OpenAI require an active internet connection.

## License

This project is licensed under the MIT License.

## Contact

For any issues or questions, please contact kyle at [kyle.marino22@gmail.com].
