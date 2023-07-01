import cv2
import mediapipe as mp
from collections import Counter

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
    max_num_hands=2
)

cap = cv2.VideoCapture(2)
w = 640
h = 480

up = 0


def find_position(frame):
    list_hand = []
    results = hands.process(frame)
    if results.multi_hand_landmarks is not None:
        for landmarks in results.multi_hand_landmarks:
            for i, pt in enumerate(landmarks.landmark):
                x = int(pt.x * w)
                y = int(pt.y * h)
                list_hand.append([i, x, y])

    return list_hand


def find_up(position):
    a = position
    up = 0
    tip = [8, 12, 16, 20]
    if len(a) != 0:
        # check for if enough data presents in the list
        for id in range(0, 4):
            if a[tip[id]][2] and a[tip[id] - 2][2] != 0:
                data_completion = 1
            else:
                data_completion = 0

        if data_completion != 0:
            finger = []
            # process thumb (works for only right hand)
            if a[3][1] < a[4][1]:
                finger.append(1)
            else:
                finger.append(0)

            fingers = []
            # process the rest of the fingers
            for id in range(0, 4):
                if a[tip[id]][2] < a[tip[id] - 1][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            x = fingers + finger
            c = Counter(x)
            up = c[1]

    return up

