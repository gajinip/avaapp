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

SCREEN_W, SCREEN_H = pyautogui.size()
prev_x, prev_y = 0, 0
smooth_factor = 5


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
        h, w, _ = frame.shape

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


            if ava.mouse_mode:
                if f == [0, 1, 0, 0, 0]: # Index finger up
                    
                    margin = 118
                    
                    # 2. Map coordinates (Assuming standard 640x480 webcam)
                    # We map [110 to 530] in camera -> [0 to 1920] on screen
                                        
                    
                    
                    target_x = np.interp(hand_landmarks.landmark[8].x * w, [margin, w - margin], [0, SCREEN_W])
                    target_y = np.interp(hand_landmarks.landmark[8].y * h, [margin, h - margin], [0, SCREEN_H])


                    target_x = np.clip(target_x, 0, SCREEN_W)
                    target_y = np.clip(target_y, 0, SCREEN_H)
                    
                    # 3. Apply Smoothing (Removes jitter)
                    global prev_x, prev_y
                    curr_x = prev_x + (target_x - prev_x) / smooth_factor
                    curr_y = prev_y + (target_y - prev_y) / smooth_factor
                    
                    # 4. Final Move (Duration=0 for instant response)
                    pyautogui.moveTo(curr_x, curr_y, duration=0)
                    prev_x, prev_y = curr_x, curr_y

                elif f == [0, 0, 0, 0, 0]: # Fist to click
                    pyautogui.click()
                    time.sleep(0.3)

            # --- 1. VOLUME CONTROL (Index, Middle, Ring UP) ---
            # --- 1. VOLUME CONTROL ---
            if f == [0, 0, 1, 1, 1]:
    # Clamp the input to the interpolation range (0.3 to 0.7)
                hand_y = np.clip(hand_landmarks.landmark[8].y, 0.3, 0.7)
                vol_level = np.interp(hand_y, [0.3, 0.7], [max_vol, min_vol])
                volume.SetMasterVolumeLevel(vol_level, None)
    # Ensure vol_level is within hardware bounds
                # Change this line in main.py:
                vol_per = np.interp(vol_level, [min_vol, max_vol], [0, 100])
                vol_bar = np.interp(vol_level, [min_vol, max_vol], [400, 150]) # Calculate percentage
                cv2.putText(frame, f"VOL: {int(vol_per)}%", (40, 450), 1, 2, (255, 0, 0), 2)
                cv2.rectangle(frame, (50, 150), (85, 400), (255, 0, 0), 3)
                cv2.rectangle(frame, (50, int(vol_bar)), (85, 400), (255, 0, 0), cv2.FILLED)
 
            # --- 2. BRIGHTNESS CONTROL (Index + Pinky UP) ---
            elif f == [1, 1, 0, 0, 1]:
                bright_level = int(np.interp(hand_landmarks.landmark[8].y, [0.3, 0.7], [100, 0]))
                sbc.set_brightness(max(0, min(100, bright_level)))
                # Visuals
                bright_bar = np.interp(bright_level, [0, 100], [400, 150])
                cv2.rectangle(frame, (590, 150), (625, 400), (0, 255, 255), 3)
                cv2.rectangle(frame, (590, int(bright_bar)), (625, 400), (0, 255, 255), cv2.FILLED)
                cv2.putText(frame, f"BRIGHT: {bright_level}%", (500, 450), 1, 1, (0, 255, 255), 2)

            # --- 3. COOLDOWN ACTIONS ---
            elif now - last_action_time > 1.5:
                # VOICE (Only Index UP)
                if f == [0,1,0,0,0] and ava.mouse_mode == False:
                    if not ava.running:
                        threading.Thread(target=ava.run, daemon=True).start()
                        last_action_time = now

                # MINIMIZE (Index + Middle UP)
                elif f == [0,1,1,0,0] and ava.mouse_mode == False:
                    pyautogui.hotkey("win", "down")
                    pyautogui.hotkey("win", "down")
                    last_action_time = now

                # SCROLLING
                elif sum(f) == 4 : # Open hand
                    pyautogui.scroll(300)
                elif sum(f) == 0 : # Fist
                    pyautogui.scroll(-300)

        cv2.imshow("AVA – Universal Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_gesture()