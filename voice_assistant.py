import speech_recognition as sr
import pyttsx3
import webbrowser
import subprocess
import os

class AVA:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 170) # Slightly faster is usually more natural
        self.recognizer = sr.Recognizer()
        self.running = False

    def speak(self, text):
        print(f"AVA: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            # Adjusting for 0.5 seconds helps in noisy rooms
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                # Stops waiting for speech after 5s; stops recording after 10s
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio).lower()
                print(f"User: {text}")
                return text
            except (sr.UnknownValueError, sr.WaitTimeoutError):
                return ""
            except Exception as e:
                print(f"Error: {e}")
                return ""

    def run(self):
        self.running = True
        self.speak("System active. How can I help?")

        while self.running:
            text = self.listen()
            if not text:
                continue

            if "search for" in text:
                query = text.replace("search for", "").strip()
                self.speak(f"Searching for {query}")
                webbrowser.open(f"https://www.google.com/search?q={query}")

            elif "open youtube" in text:
                self.speak("Opening YouTube")
                webbrowser.open("https://youtube.com")

            elif "open browser" in text:
                self.speak("Opening Chrome")
                # Using 'start' on Windows is safer for launching apps
                os.system("start chrome") 

            elif "stop" in text or "sleep" in text:
                self.speak("Going to sleep. Goodbye!")
                self.running = False