from faster_whisper import WhisperModel
import os

# Initialize Whisper model globally to avoid reloading for each request
# 'base' model is a good balance for MVP. 'tiny' or 'small' are faster but less accurate.
# device="cpu" for broader compatibility, "cuda" if you have an NVIDIA GPU.
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        print("Loading Whisper model (base)... This may take a moment.")
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8") # int8 for CPU optimization
        print("Whisper model loaded.")
    return _whisper_model

async def transcribe_audio(audio_file_path: str) -> str:
    """Transcribes an audio file to text."""
    model = get_whisper_model()
    # segments, info = model.transcribe(audio_file_path, beam_size=5) # Default beam_size is 5
    # For MVP, a simpler transcription might be faster
    segments, info = model.transcribe(audio_file_path)
    
    transcription = " ".join([segment.text for segment in segments])
    print(f"Transcribed '{os.path.basename(audio_file_path)}': '{transcription}'")
    return transcription
