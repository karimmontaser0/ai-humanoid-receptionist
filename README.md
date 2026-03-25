# 🤖 Hamada: AI Egyptian Receptionist 🇪🇬

> A conversational AI assistant with a localized Egyptian personality. This project integrates Speech-to-Text, Generative AI, and high-quality Text-to-Speech into a sleek Tkinter GUI.

## ✨ Key Features
* **🗣️ Localized Personality:** Custom-prompted Gemini model acting as "Hamada," a friendly Egyptian receptionist using natural dialect.
* **🎙️ Multimodal Interaction:** Uses Google Cloud STT for recognition and ElevenLabs for high-fidelity voice.
* **📺 Interactive GUI:** Built with Tkinter, featuring full-screen background video integration via VLC.
* **🛡️ Secure Interface:** Features a password-protected exit system.

## 🛠️ Tech Stack
* **AI Models:** Google Gemini (LLM), Google Cloud STT.
* **Audio:** ElevenLabs API, SoundDevice, VLC.
* **Libraries:** `arabic_reshaper`, `python-bidi`, `python-dotenv`.

## 🚀 Quick Start
1. **Install Dependencies:** `pip install -r requirements.txt`
2. **Set API Keys:** Create a `.env` file with `GEMINI_API_KEY` and `ELEVENLABS_API_KEY`.
3. **Run:** `python main.py`

---
## 🎥 Live Demo
👉 **[View AI Robot Demo](https://karimmontaser0.github.io/My_Portfolio/)**