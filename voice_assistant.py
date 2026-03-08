import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import pyautogui

class AVA:

    logs = []

    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 170) # Slightly faster is usually more natural
        self.recognizer = sr.Recognizer()
        self.running = False
        self.mouse_mode = False
        self.mode = "idle"

    def add_log(self,text):
        print(text)
        self.logs.append(text)
        if len(self.logs) > 20:
            self.logs.pop(0)

    def speak(self, text):
        self.mode = "speak"
        print(f"AVA: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        self.mode = "listening"
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.add_log("Listening...")
            try:
                # Timeout prevents the thread from hanging
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                self.mode = "idle"
                return ""

        try:
            self.add_log("Recognizing...") # Visual feedback for logs
            text = self.recognizer.recognize_google(audio).lower()
            self.add_log(f"User: {text}") 
            return text
        except sr.UnknownValueError:
            self.add_log("AVA: I didn't catch that.")
            self.mode = "idle"
            return ""
        except sr.RequestError:
            self.add_log("AVA: API Error. Check connection.")
            self.mode = "idle"
            return ""

    def run(self):
        self.running = True
        self.speak("System active. How can I help?")

        while self.running:
            text = self.listen()

            if not text:
                continue

            if "on" in text:
                    self.mouse_mode = True
                    self.speak("Mouse control activated")
            elif "off mouse mode" in text:
                    self.mouse_mode = False
                    self.speak("Mouse control deactivated")

            if "search for" in text:
                query = text.replace("search for", "").strip()
                self.speak(f"Searching for {query}")
                webbrowser.open(f"https://www.google.com/search?q={query}")

            elif "close window" in text:
                query = text.replace("close", "").strip()
                self.speak(f"closing {query}")
                pyautogui.hotkey('alt','f4')


            elif "open youtube" in text:
                self.speak("Opening YouTube")
                webbrowser.open("https://youtube.com")

            elif "open browser" in text:
                self.speak("Opening Chrome")
                os.system("start chrome") 

            elif "open" in text:
                query = text.replace("open"," ").strip()
                self.speak(f"opening {query}")
                os.system(f"start {query}")

            elif "stop" in text or "sleep" in text:
                self.speak("Going to sleep. Goodbye!")
                self.running = False