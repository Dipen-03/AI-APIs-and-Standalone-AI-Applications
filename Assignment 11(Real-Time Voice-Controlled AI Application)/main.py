import os
import time
import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
from gtts import gTTS
from google import genai

# Initialize GenAI Client
client = genai.Client()

def record_audio(filename="input_temp.wav", duration=5, fs=16000):
    """Records microphone audio using sounddevice and saves it as a WAV file."""
    print(f"\nListening for {duration} seconds... Speak now!")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording finishes
    wav.write(filename, fs, audio_data)
    print("Recording complete. Processing...")
    return filename

def speak_text(text):
    """Converts text to speech and plays it using Windows native media handler."""
    tts_start = time.time()
    
    tts = gTTS(text=text, lang='en', slow=False)
    temp_audio = "temp_ai_response.mp3"
    tts.save(temp_audio)
    
    tts_time_to_first_audio = time.time() - tts_start
    
    # Play audio using Windows native file handler (no pygame needed!)
    os.startfile(temp_audio)
    
    # Wait a few seconds for playback to finish before cleaning up
    time.sleep(4)
    
    if os.path.exists(temp_audio):
        os.remove(temp_audio)
        
    return tts_time_to_first_audio

def run_voice_assistant():
    print("\n=== Voice-Controlled AI Assistant Active ===")
    
    try:
        # --- STAGE 1: RECORD & STT ---
        stt_start = time.time()
        audio_file = record_audio(duration=5)
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            transcript = recognizer.recognize_google(audio_data)
            
        stt_delay = time.time() - stt_start
        print(f"User Transcript: '{transcript}'")
        
        if os.path.exists(audio_file):
            os.remove(audio_file)
        
        # --- STAGE 2: AI PROCESSING (LLM) ---
        print("Thinking (AI Response)...")
        ai_start = time.time()
        
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=f"You are a helpful, concise voice assistant. Answer this query in 1 to 2 short sentences max: {transcript}",
        )
        ai_reply = response.text.strip()
        ai_delay = time.time() - ai_start
        print(f"AI Response: '{ai_reply}'")
        
        # --- STAGE 3: TTS & PLAYBACK ---
        print("Generating voice output...")
        tts_delay = speak_text(ai_reply)
        
        # --- METRICS SUMMARY ---
        total_delay = stt_delay + ai_delay + tts_delay
        print("\n--- Latency Metrics ---")
        print(f"STT Delay: {stt_delay:.3f}s")
        print(f"AI/LLM Processing Delay: {ai_delay:.3f}s")
        print(f"TTS Time-to-First-Audio: {tts_delay:.3f}s")
        print(f"Total End-to-End Delay: {total_delay:.3f}s")

    except sr.UnknownValueError:
        print("Error: Could not understand the audio (check background noise).")
    except sr.RequestError as e:
        print(f"Network Error: Could not request results from STT service; {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY environment variable is not set!")
        print("Set it in your terminal using: $env:GEMINI_API_KEY='your_api_key'")
    else:
        run_voice_assistant()