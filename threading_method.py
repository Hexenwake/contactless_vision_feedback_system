import tkinter as tk
import cv2
from PIL import Image, ImageTk
from module import find_position
import threading
from collections import Counter
import queue
from datetime import datetime, date
import time
from pymouse import PyMouse
from pykeyboard import PyKeyboard


def get_hand(frame_resized):
    up = 0
    tip = [8, 12, 16, 20]
    a = find_position(frame_resized)

    # hand counting algorithm
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
        else:
            up = 0
    return up


global up_list
up_list = []
global period
period = 10


def display_video():
    while True:
        try:
            frame = video_queue.get_nowait()
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            photo = ImageTk.PhotoImage(image)
            camera_frame.configure(image=photo)
            camera_frame.image = photo
        except queue.Empty:
            pass

        # camera_frame.after(15, display_video)


def process_frame():
    while True:
        try:
            global period
            global up_list
            frame = video_queue.get_nowait()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # frame_resized = cv2.resize(frame, (640, 480))
            # logic
            if period != 0:
                up_list.append(get_hand(frame))
                period = period - 1
            else:
                print("end result")
                up = max(up_list)
                print(up)
                key_press(up)
                up_list = []
                period = 10

        except queue.Empty:
            pass
        # camera_frame.after(1, process)


def key_press(final_up):
    if final_up > 0:
        if final_up == 1:
            keyboard.press_key('1')
        elif final_up == 2:
            keyboard.press_key('2')
        elif final_up == 3:
            keyboard.press_key('3')
        elif final_up == 4:
            keyboard.press_key('4')
        elif final_up == 5:
            keyboard.press_key('5')
        time.sleep(1.5)


def video_capture():
    while True:
        ret, frame = cap.read()
        if ret:
            video_queue.put(frame)


def show_question(index):
    global questions
    question_label = tk.Label(questions_frame, text="")
    question_label.pack()
    current_question = questions[index]
    question_label.config(text=f"Question {index + 1}: {current_question['question']}")

    i = 0
    buttons = []
    for options in questions[index]['options']:
        button = tk.Button(questions_frame, text=options, command=lambda data=options: handle_answer(data))
        buttons.append(button)
        button.pack()
        window.bind(str(i + 1), lambda e, data=options: handle_answer(data))
        i = i + 1

    previous_button = tk.Button(questions_frame, text="Previous", command=previous_question)
    previous_button.pack(side=tk.BOTTOM, padx=5, pady=10)

    next_button = tk.Button(questions_frame, text="Next", command=next_question)
    next_button.pack(side=tk.BOTTOM, padx=5)


def handle_answer(answer):
    print("Selected answer:", answer)


def next_question():
    global current_index
    current_index = (current_index + 1) % len(questions)

    destroy_widget()
    show_question(current_index)


def previous_question():
    global current_index
    current_index = (current_index - 1) % len(questions)

    destroy_widget()
    show_question(current_index)


def destroy_widget():
    for widget in questions_frame.winfo_children():
        widget.destroy()


# declaration
global current_index
current_index = 0

global questions
questions = [
    {
        'question': 'What is the capital of France?',
        'options': ['London', 'Paris', 'Berlin']
    },
    {
        'question': 'Which country has the largest population?',
        'options': ['China', 'India', 'United States']
    },
    {
        'question': 'What is the currency of Japan?',
        'options': ['Yuan', 'Rupee', 'Yen']
    }
]

mouse = PyMouse()
keyboard = PyKeyboard()

# Create the main window
window = tk.Tk()
window.bind('<Escape>', lambda e: window.quit())

questions_frame = tk.Frame(window)
questions_frame.pack(side=tk.LEFT)
questions_frame.configure(height=500, width=500)

# Create a camera frame
camera_frame = tk.Label(window)
camera_frame.pack(side=tk.LEFT)
camera_frame.configure(width=500, height=500)

# Open the camera
cap = cv2.VideoCapture(3)

video_queue = queue.Queue()
hand_count_queue = queue.Queue()

video_thread = threading.Thread(target=display_video)
processing_thread = threading.Thread(target=process_frame)
capture_thread = threading.Thread(target=video_capture)
questions_thread = threading.Thread(target=show_question, args=(current_index,))

video_thread.start()
processing_thread.start()
capture_thread.start()
questions_thread.start()

window.mainloop()
