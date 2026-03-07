import mediapipe as mp

class vision:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

    def fingers(self, hand_landmarks, hand_label):
        """
        Returns finger state: [thumb, index, middle, ring, pinky]
        1 = up, 0 = down
        """
        fingers = []
        
        # Improved Thumb logic: Depends on Hand Label (Left vs Right)
        # For Right hand, Tip.x < Knuckle.x is UP. For Left, Tip.x > Knuckle.x is UP.
        if hand_label == "Right":
            fingers.append(1 if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x else 0)
        else:
            fingers.append(1 if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x else 0)

        # 4 Fingers: Check if tip is above the PIP joint
        tips = [8, 12, 16, 20]
        for tip in tips:
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers