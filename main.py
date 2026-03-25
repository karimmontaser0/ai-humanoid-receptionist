import os
import io
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import vlc
import platform
import threading
import sounddevice as sd
import numpy as np
import re
import subprocess
import requests
import arabic_reshaper
from bidi.algorithm import get_display
from scipy.io.wavfile import write
from google.cloud import speech
import google.generativeai as genai
from dotenv import load_dotenv

# Load API Keys from .env file
load_dotenv()

# Configuration
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_stt.json"
INPUT_DEVICE_INDEX = 2  # Mic
OUTPUT_DEVICE_INDEX = 2 # Speaker
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")

client = speech.SpeechClient()

def record_audio(duration=5, samplerate=16000):
    try:
        sd.default.device = (INPUT_DEVICE_INDEX, OUTPUT_DEVICE_INDEX)
        recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()
        return recording.flatten(), samplerate
    except Exception as e:
        print(f"❌ Recording error: {e}")
        return np.zeros(int(samplerate * duration)), samplerate

def transcribe_google(audio_data, sample_rate):
    try:
        audio_bytes = audio_data.tobytes()
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code="ar-EG"
        )
        response = client.recognize(config=config, audio=audio)
        if response.results:
            text = response.results[0].alternatives[0].transcript
            print("📃 Arabic Detected:", text)
            return text
        return ""
    except Exception as e:
        print("❌ STT Error:", e)
        return ""

def reshape_arabic(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

class AI_Assistant:
    def __init__(self):
        self.elevenlabs_api_key = ELEVEN_KEY
        self.voice_id = "UR972wNGq3zluze0LoIp"
        self.update_response_label = None
        self.keep_listening = False
        genai.configure(api_key=GEMINI_KEY)
        self.gemini_model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

    def listen_loop(self):
        self.keep_listening = True
        while self.keep_listening:
            audio, rate = record_audio()
            user_text = transcribe_google(audio, rate)
            if user_text:
                self.generate_ai_response(user_text)

    def stop_listening(self):
        self.keep_listening = False

    def generate_ai_response(self, user_text):
        try:
            prompt = (
                "You are a helpful Egyptian receptionist named Hamada. "
                "Respond in Egyptian Arabic (Egyptian dialect) only. "
                "Use natural Egyptian expressions. Be friendly. "
                f"السؤال: {user_text}\nالإجابة بالمصري:"
            )
            response = self.gemini_model.generate_content(prompt)
            ai_response = response.text.strip()
            self.generate_audio(ai_response)
        except Exception as e:
            self.generate_audio("آسف، حصل خطأ. عايز تجرب تاني؟")

    def generate_audio(self, text):
        cleaned_text = re.sub(r"[\*_]", "", text)
        reshaped = reshape_arabic(cleaned_text)
        if self.update_response_label:
            self.update_response_label(reshaped)

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"
        headers = {"xi-api-key": self.elevenlabs_api_key, "Content-Type": "application/json"}
        data = {
            "text": cleaned_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.6, "similarity_boost": 0.8},
            "stream": True,
        }
        try:
            response = requests.post(url, json=data, headers=headers, stream=True)
            if response.status_code == 200:
                player = subprocess.Popen(
                    ["ffplay", "-nodisp", "-autoexit", "-af", "atempo=1.0", "-f", "alsa", "-i", "hw:2,0", "-"],
                    stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                for chunk in response.iter_content(chunk_size=1024):
                    player.stdin.write(chunk)
                player.stdin.close()
                player.wait()
        except Exception as e:
            print("🔊 Audio Exception:", e)

class ReceptionistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Receptionist")
        self.root.attributes("-fullscreen", True)
        self.video_panel = tk.Frame(root, bg="black")
        self.video_panel.pack(fill=tk.BOTH, expand=1)

        self.instance = vlc.Instance("--no-video-title-show", "--fullscreen", "--no-audio")
        self.player = self.instance.media_player_new()
        # Make sure backgroundd.mp4 is in the same folder
        if os.path.exists("backgroundd.mp4"):
            media = self.instance.media_new("backgroundd.mp4")
            media.add_option("input-repeat=65535")
            self.player.set_media(media)

        if platform.system() == "Windows":
            self.player.set_hwnd(self.video_panel.winfo_id())
        else:
            self.player.set_xwindow(self.video_panel.winfo_id())
        self.player.play()

        self.start_btn = ttk.Button(self.video_panel, text="🎤 Start", command=self.start_chat)
        self.start_btn.place(relx=0.4, rely=0.9, anchor=tk.CENTER)
        
        self.stop_btn = ttk.Button(self.video_panel, text="🛑 Stop", command=self.stop_chat)
        self.stop_btn.place(relx=0.6, rely=0.9, anchor=tk.CENTER)

        self.response_label = tk.Label(self.video_panel, text="", font=("Arial", 20), bg="black", fg="white", wraplength=900)
        self.response_label.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        self.assistant = AI_Assistant()
        self.assistant.update_response_label = self.update_response_label

    def start_chat(self):
        threading.Thread(target=self.assistant.listen_loop, daemon=True).start()

    def stop_chat(self):
        self.assistant.stop_listening()

    def update_response_label(self, text):
        self.response_label.config(text=text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ReceptionistApp(root)
    root.mainloop()