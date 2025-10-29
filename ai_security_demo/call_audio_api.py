import requests
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python call_audio_api.py <audio_file_path>", file=sys.stderr)
        sys.exit(1)

    audio_file_path = sys.argv[1]
    api_url = "http://localhost:8000/audio_query" # Ensure this matches your FastAPI URL

    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found at {audio_file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(audio_file_path, "rb") as f:
            # Adjust mimetype if your audio files are not mp3 (e.g., 'audio/wav')
            files = {'audio_file': (os.path.basename(audio_file_path), f, 'audio/mpeg')}
            response = requests.post(api_url, files=files)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            print(response.text) # Print the API response to stdout for promptfoo to capture
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
