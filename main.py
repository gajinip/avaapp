import cv2
import pyautogui
import threading
import time
import numpy as np
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from gesture_controller import vision
from voice_assistant import AVA 

# ================== INITIALIZATION ==================
v = vision()
ava = AVA()
last_action_time = 0

# ================== AUDIO INITIALIZATION ==================
# This specific method targets the default speaker directly
device_enumerator = AudioUtilities.GetDeviceEnumerator()
default_speakers = device_enumerator.GetDefaultAudioEndpoint(0, 0) # 0, 0 = Render, Multimedia
interface = default_speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get volume range
vol_range = volume.GetVolumeRange()  # Usually (-65.25, 0.0)
min_vol, max_vol = vol_range[0], vol_range[1]
def run_gesture():
    global last_action_time
    cap = cv2.VideoCapture(0)
    
    # Smooth bar variables
    vol_bar = 400
    bright_bar = 400

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = v.hands.process(rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            # Extract hand label (Left/Right) for thumb logic
            hand_label = results.multi_handedness[0].classification[0].label
            
            v.mp_draw.draw_landmarks(frame, hand_landmarks, v.mp_hands.HAND_CONNECTIONS)
            f = v.fingers(hand_landmarks, hand_label)
            now = time.time()

            # --- 1. VOLUME CONTROL (Index, Middle, Ring UP) ---
            if f[1] == 1 and f[2] == 1 and f[3] == 1 and f[4] == 0:
                # Map hand height to volume levels
                vol_level = np.interp(hand_landmarks.landmark[8].y, [0.2, 0.8], [max_vol, min_vol])
                volume.SetMasterVolumeLevel(vol_level, None)
                
                # Visuals
                perc = int(np.interp(vol_level, [min_vol, max_vol], [0, 100]))
                vol_bar = np.interp(vol_level, [min_vol, max_vol], [400, 150])
                cv2.rectangle(frame, (50, 150), (85, 400), (255, 0, 0), 3)
                cv2.rectangle(frame, (50, int(vol_bar)), (85, 400), (255, 0, 0), cv2.FILLED)
                cv2.putText(frame, f"VOL: {perc}%", (40, 450), 1, 2, (255, 0, 0), 2)

            # --- 2. BRIGHTNESS CONTROL (Index + Pinky UP) ---
            elif f[1] == 1 and f[4] == 1 and f[2] == 0:
                bright_level = int(np.interp(hand_landmarks.landmark[8].y, [0.2, 0.8], [100, 0]))
                sbc.set_brightness(max(0, min(100, bright_level)))
                
                # Visuals
                bright_bar = np.interp(bright_level, [0, 100], [400, 150])
                cv2.rectangle(frame, (590, 150), (625, 400), (0, 255, 255), 3)
                cv2.rectangle(frame, (590, int(bright_bar)), (625, 400), (0, 255, 255), cv2.FILLED)
                cv2.putText(frame, f"BRIGHT: {bright_level}%", (500, 450), 1, 1, (0, 255, 255), 2)

            # --- 3. COOLDOWN ACTIONS ---
            elif now - last_action_time > 1.5:
                # VOICE (Only Index UP)
                if f[1] == 1 and sum(f[2:]) == 0 :
                    if not ava.running:
                        threading.Thread(target=ava.run, daemon=True).start()
                        last_action_time = now

                # MINIMIZE (Index + Middle UP)
                elif f[1] == 1 and f[2] == 1 and f[3] == 0:
                    pyautogui.hotkey("win", "d")
                    last_action_time = now

                # SCROLLING
                elif sum(f[1:]) == 4: # Open hand
                    pyautogui.scroll(400)
                elif sum(f[1:]) == 0: # Fist
                    pyautogui.scroll(-400)

        cv2.imshow("AVA – Universal Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_gesture()