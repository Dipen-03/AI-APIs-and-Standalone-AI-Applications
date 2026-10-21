import time
import os
import speech_recognition as sr
from gtts import gTTS
from deep_translator import MyMemoryTranslator

def run_voice_interpreter():
    recognizer = sr.Recognizer()
    
    try:
        # --- Stage 1: Record Audio ---
        print("\nListening...")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            start_record = time.time()
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        # --- Stage 2: Transcribe Speech (STT) ---
        t_stt_start = time.time()
        transcript = recognizer.recognize_google(audio_data, language="en-US")
        t_stt_end = time.time()
        stt_delay = t_stt_end - t_stt_start
        print(f"Transcript: '{transcript}'")

        # --- Stage 3: Translate Text (Using MyMemory) ---
        t_trans_start = time.time()
        # Using MyMemoryTranslator with full language names
        translated_text = MyMemoryTranslator(source='english us', target='french').translate(transcript)
        t_trans_end = time.time()
        translation_delay = t_trans_end - t_trans_start
        print(f"Translated (French): '{translated_text}'")

        # --- Stage 4: Generate Speech (TTS) ---
        t_tts_start = time.time()
        tts = gTTS(text=translated_text, lang='fr', slow=False)
        temp_audio_file = "temp_output.mp3"
        tts.save(temp_audio_file)
        t_tts_end = time.time()
        tts_time = t_tts_end - t_tts_start

        # --- Stage 5: Play Audio ---
        print("Playing audio...")
        play_start = time.time()
        os.startfile(temp_audio_file)
        time.sleep(3) 
        play_end = time.time()
        
        total_delay = play_end - start_record

        # Print stage metrics
        print(f"\n--- Latency Metrics ---")
        print(f"STT Delay: {stt_delay:.3f}s")
        print(f"Translation Delay: {translation_delay:.3f}s")
        print(f"TTS Time-to-First-Audio: {tts_time:.3f}s")
        print(f"Total Delay: {total_delay:.3f}s")

    except sr.WaitTimeoutError:
        print("Error: No speech detected within the timeout period.")
    except sr.UnknownValueError:
        print("Error: Could not understand the audio.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_voice_interpreter()