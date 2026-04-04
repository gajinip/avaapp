import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import pyautogui
import threading
import time
import tempfile
import subprocess
import sys

try:
    import tkinter as tk
    from tkinter import scrolledtext
except ImportError:
    tk = None


class AVA:

    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 170)

        self.recognizer = sr.Recognizer()
        self.running = False
        self.mouse_mode = False
        self.mode = "idle"

        self.logs = []

        # UI
        self.tk_root = None
        self.preview_text_widget = None

    # ---------------- PREVIEW WINDOW ----------------
    def _preview_window_thread(self):
        self.tk_root = tk.Tk()
        self.tk_root.title("Text Preview")
        self.tk_root.geometry("700x500")

        self.preview_text_widget = scrolledtext.ScrolledText(
            self.tk_root, wrap=tk.WORD, font=("Consolas", 12)
        )
        self.preview_text_widget.pack(fill=tk.BOTH, expand=True)
        self.preview_text_widget.configure(state="disabled")

        self.tk_root.mainloop()

    def _ensure_preview_window(self):
        if not tk:
            return False

        if self.tk_root is None:
            thread = threading.Thread(target=self._preview_window_thread, daemon=True)
            thread.start()

        timeout = 5
        waited = 0
        while self.tk_root is None and waited < timeout:
            time.sleep(0.1)
            waited += 0.1

        return self.tk_root is not None

    def display_text_window(self, title, text):
        if not self._ensure_preview_window():
            return

        def update():
            try:
                self.tk_root.title(title)
                self.preview_text_widget.configure(state="normal")
                self.preview_text_widget.delete("1.0", tk.END)
                self.preview_text_widget.insert(tk.END, text)
                self.preview_text_widget.configure(state="disabled")
            except:
                pass

        self.tk_root.after(0, update)

    # ---------------- LOG ----------------
    def add_log(self, text):
        print(text)
        self.logs.append(text)
        if len(self.logs) > 20:
            self.logs.pop(0)

    # ---------------- SPEAK ----------------
    def speak(self, text):
        self.mode = "speak"
        print(f"AVA: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    # ---------------- LISTEN ----------------
    def listen(self):
        self.mode = "listening"
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.add_log("Listening...")
            self.display_text_window("Listening", "Listening...")

            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                self.mode = "idle"
                return ""

        try:
            self.add_log("Recognizing...")
            text = self.recognizer.recognize_google(audio).lower()
            self.add_log(f"User: {text}")
            self.display_text_window("You Said", text)
            return text
        except sr.UnknownValueError:
            self.add_log("AVA: I didn't catch that.")
            return ""
        except sr.RequestError:
            self.add_log("AVA: API Error. Check internet.")
            return ""

    # ---------------- FILE WRITING ----------------
    def write_to_file(self, text, filename="note.txt"):
        path = os.path.join(tempfile.gettempdir(), filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

        if sys.platform.startswith("win"):
            subprocess.Popen(["notepad.exe", path])

    # ---------------- REVIEW ----------------
    def review_text(self, text):
        if not text:
            self.speak("No text available")
            return text

        while True:
            self.display_text_window("Review", text)
            self.speak("Say change, show, or save ")
            cmd = self.listen()

            if "completed" in cmd:
                return text

            elif "show" in cmd:
                continue

            elif "change" in cmd:
                self.speak("What to change?")
                target = self.listen()

                self.speak("Replacement?")
                replacement = self.listen()

                if target and replacement and target in text:
                    text = text.replace(target, replacement, 1)
                    self.speak("Updated")

    # ---------------- ESSAY MODE ----------------
    def essay_mode(self):
        self.speak("Start speaking. Say save this file to finish")
        lines = []

        while True:
            text = self.listen()

            if not text:
                continue

            if "save this file" in text:
                break

            lines.append(text)
            self.display_text_window("Draft", "\n".join(lines))

        full = "\n".join(lines)
        full = self.review_text(full)
        self.write_to_file(full)
        self.speak("Saved")

    # ---------------- MAIN LOOP ----------------
    def run(self):
        self.running = True
        self.speak("System active. How can I help?")

        while self.running:
            text = self.listen()

            if not text:
                continue

            if "note" in text:
                self.essay_mode()

            elif "power on" in text:
                self.mouse_mode = True
                self.speak("Mouse control activated")

            elif "off mouse mode" in text:
                self.mouse_mode = False
                self.speak("Mouse control deactivated")

            elif "search on youtube " in text:
                self.speak("what to search on youtube?")
                query = self.listen()
                if query:
                    self.speak(f"Searching YouTube for {query}")
                    webbrowser.open(
                          f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                     )

            elif "search for" in text:
                self.speak("what to search for?")
                query = self.listen()
                if query:
                    self.speak(f"Searching for {query}")
                    webbrowser.open(f"https://www.google.com/search?q={query}")

            elif "close window" in text:
                self.speak("Closing window")
                pyautogui.hotkey("alt", "f4")

            elif "open" in text:
                query = text.replace("open", "").strip()
                self.speak(f"Opening {query}")
                subprocess.Popen(query, shell=True)

            elif "stop" in text or "sleep" in text:
                self.speak("Going to sleep. Goodbye!")
                self.running = False