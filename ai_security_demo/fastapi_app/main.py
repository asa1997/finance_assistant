from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import PlainTextResponse
import os
import tempfile
import ollama
from typing import Dict, Any

from .audio_utils import transcribe_audio

app = FastAPI(title="AI Security Demo API")

# Initialize Ollama client
ollama_client = ollama.Client(host='http://localhost:11434')

# --- Naive Security Defense ---
def naive_security_check(text: str) -> bool:
    """
    A simple string-based security filter.
    Returns True if malicious keywords are found, False otherwise.
    """
    malicious_keywords = ["transfer funds", "send money", "wire funds", "move money"]
    normalized_text = text.lower()
    is_malicious = any(keyword in normalized_text for keyword in malicious_keywords)
    if is_malicious:
        print(f"Naive filter BLOCKED: '{text}'")
    else:
        print(f"Naive filter ALLOWED: '{text}'")
    return is_malicious

# --- AI Brain (Llama 3) Interaction ---
async def get_llama_response(prompt: str) -> str:
    """Sends a prompt to Llama 3 and returns its response."""
    try:
        print(f"Calling Llama 3 with prompt: '{prompt}'")
        response: Dict[str, Any] = ollama_client.chat(
            model='llama3.2:latest',
            messages=[{'role': 'user', 'content': prompt}]
        )
        content = response['message']['content']
        print(f"Llama 3 response: '{content[:100]}...'") # Log first 100 chars
        return content
    except Exception as e:
        print(f"Error calling Llama 3: {e}")
        return "I'm sorry, I couldn't process your request at the moment due to an internal error."

# --- API Endpoints ---

@app.post("/text_query", response_class=PlainTextResponse)
async def text_query(text: str):
    """
    Processes a text query. Applies naive defense, then Llama 3.
    """
    if naive_security_check(text):
        return "Blocked by naive security filter: Malicious keywords detected."
    
    response = await get_llama_response(text)
    return response

@app.post("/audio_query", response_class=PlainTextResponse)
async def audio_query(audio_file: UploadFile = File(...)):
    """
    Processes an audio query. Transcribes, applies naive defense, then Llama 3.
    """
    # Save the uploaded audio file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(await audio_file.read())
        tmp_file_path = tmp_file.name
    
    try:
        # Transcribe the audio
        transcription = await transcribe_audio(tmp_file_path)
        
        # Apply naive security check to the transcription
        if naive_security_check(transcription):
            return "Blocked by naive security filter (after transcription): Malicious keywords detected."
        
        # Get Llama 3 response based on transcription
        response = await get_llama_response(transcription)
        return response
    except Exception as e:
        print(f"Error processing audio query: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process audio: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "FastAPI is running"}
