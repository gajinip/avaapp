# AVA – Automated Voice Assistant & Gesture Controller

AVA is a Python-based universal system controller that allows you to manage your PC using hand gestures and voice commands. By integrating **MediaPipe** for computer vision and **SpeechRecognition** for voice processing, AVA provides a "hands-free" interaction model for common tasks.

## 🚀 Features

### ✋ Hand Gesture Control

Control system parameters and navigate your OS with simple hand movements:

* **Volume Control**: Adjust master volume by moving your index finger vertically while holding up three fingers (Index, Middle, Ring).
* **Brightness Control**: Adjust screen brightness using the Index and Pinky finger gesture.
* **Minimize Windows**: Quickly show desktop using the "Victory" sign (Index + Middle UP).
* **Scrolling**: Scroll up with an open hand and scroll down with a closed fist.

### 🎙️ Voice Assistant (AVA)

Activate the assistant by holding up only your index finger to perform tasks:

* **Web Automation**: Search Google or open YouTube instantly.
* **App Launcher**: Open browsers (Chrome) or system applications by voice.
* **Mouse Mode**: Toggle specialized mouse control modes.
* **System Sleep**: Put the assistant into standby mode.

---

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone https://github.com/gajini1507/avaapp.git
cd avaapp

```


2. **Install dependencies**:
Ensure you have Python 3.8+ installed, then run:
```bash
pip install -r requirements.txt

```


3. **System Requirements**:
* A working Webcam for gesture detection.
* A Microphone for voice commands.
* Windows OS (required for `pycaw` and `screen-brightness-control`).



---

## 📖 Usage

Run the main application to start the camera and the gesture listener:

```bash
python main.py

```

### Gesture Guide

| Action | Gesture Pattern |
| --- | --- |
| **Volume Up/Down** | Index + Middle + Ring UP |
| **Brightness Up/Down** | Index + Pinky UP |
| **Voice Command** | Index Finger UP (Hold) |
| **Minimize All** | Index + Middle UP (Victory Sign) |
| **Scroll Up** | All fingers open |
| **Scroll Down** | All fingers closed (Fist) |

---

## 📂 Project Structure

* `main.py`: The central hub that integrates camera feed, gesture logic, and voice triggers.
* 
`gesture_controller.py`: Contains the `vision` class for processing hand landmarks and finger states using MediaPipe.


* `voice_assistant.py`: Contains the `AVA` class for speech-to-text and command execution.
* `requirements.txt`: List of necessary libraries including `opencv-python`, `mediapipe`, `pycaw`, and `pyttsx3`.

