import tkinter as tk
import customtkinter as ct
import cv2
import threading
import queue
import time
from datetime import datetime, date

from collections import Counter
from pymouse import PyMouse
from pykeyboard import PyKeyboard
from covifs_db import RealtimeFirebaseGet, RealtimeFirebaseUpload
from PIL import Image, ImageTk
from module import find_position


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
            keyboard.tap_key('1')
        elif final_up == 2:
            keyboard.tap_key('2')
        elif final_up == 3:
            keyboard.tap_key('3')
        elif final_up == 4:
            keyboard.tap_key('4')
        elif final_up == 5:
            keyboard.tap_key('5')
        time.sleep(1.6)


def video_capture():
    while True:
        ret, frame = cap.read()
        if ret:
            video_queue.put(frame)


def landing_page():
    destroy_widget()
    global questions, img_hand_5_path, img_hand_1_path, tk_image_5, tk_image_1
    global img_path_array, intro_img, current_index

    upper_frame = tk.Frame(questions_frame, width=500, height=430)
    upper_frame.grid(row=1, column=1)

    resized = intro_img.resize((500, 430), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(resized)
    label = tk.Label(upper_frame, image=photo)
    label.image = photo
    label.grid(row=1, column=1)

    lower_frame = tk.Frame(questions_frame)
    lower_frame.grid(row=2, column=1)

    next_button = tk.Button(lower_frame, text="Continue", command=lambda i=current_index: show_question(i))
    tk_image_5 = image_handler(img_hand_5_path)
    next_button.configure(compound="left", image=tk_image_5)
    next_button.grid(row=1, column=2)
    window.bind(str(5), lambda e, i=current_index: show_question(i))

    next_button = tk.Button(lower_frame, text="Good Review", command=lambda i=current_index: good_review())
    tk_image_1 = image_handler(img_hand_1_path)
    next_button.configure(compound="left", image=tk_image_1)
    next_button.grid(row=1, column=1)
    window.bind(str(1), lambda e, i=current_index: good_review())


def show_question(index):
    destroy_widget()
    global questions, img_hand_5_path, img_hand_4_path, tk_image_4, tk_image_5, tk_img_array
    global img_path_array3
    tk_img_array = set_images(img_path_array)

    question_label = tk.Label(questions_frame, text="")
    question_label.grid(row=0, column=3)
    question_label.config(text="What would seem to be the problem?")

    def select_option(option):
        radio_var.set(option)
        handle_answer(option)
        print("Selected Option:", option)

    i = 0
    radio_var = tk.StringVar()
    for options in questions[index]:
        radio_button = tk.Radiobutton(questions_frame, text=options, variable=radio_var, value=options,
                                      command=lambda data=options: handle_answer(data))
        radio_button.configure(compound="right", image=tk_img_array[i])
        radio_button.grid(row=i + 2, column=3, padx=10, pady=10)
        window.bind(str(i + 1), lambda e, data=options: select_option(data))
        i = i + 1

    previous_button = tk.Button(questions_frame, text="Previous", command=previous_question)
    tk_image_4 = image_handler(img_hand_4_path)
    previous_button.config(compound="left", image=tk_image_4)
    previous_button.grid(row=5, column=2, padx=10)
    window.bind(str(4), lambda e: previous_question())

    next_button = tk.Button(questions_frame, text="Next", command=next_question)
    tk_image_5 = image_handler(img_hand_5_path)
    next_button.configure(compound="left", image=tk_image_5)
    next_button.grid(row=5, column=4, padx=10)
    window.bind(str(5), lambda e: next_question())


def ending_page():
    destroy_widget()
    global tk_image_5
    global img_path_array, resized_ed_img, reviews

    upper_frame = tk.Frame(questions_frame, width=500, height=430)
    upper_frame.grid(row=1, column=1)

    photo = ImageTk.PhotoImage(resized_ed_img)
    label = tk.Label(upper_frame, image=photo)
    label.image = photo
    label.grid(row=1, column=1)

    lower_frame = tk.Frame(questions_frame)
    lower_frame.grid(row=2, column=1)

    next_button = tk.Button(lower_frame, text="Continue", command=landing_page)
    tk_image_5 = image_handler(img_hand_5_path)
    next_button.configure(compound="left", image=tk_image_5)
    next_button.grid(row=1, column=2)
    window.bind(str(5), lambda e: landing_page())
    obtain_time()
    print(reviews)
    rfu.upload(reviews)
    reviews = {}


def obtain_time():
    global reviews
    today = date.today()
    now = datetime.now()
    time_now = now.strftime("%H:%M:%S")
    date_today = today.strftime("%d:%m:%Y")

    reviews["time"] = time_now
    reviews["date"] = date_today


def image_handler(path, width=50, height=50):
    image = Image.open(path)
    resized_image = image.resize((width, height))
    res_img = ImageTk.PhotoImage(resized_image)
    return res_img


def set_images(path_array):
    res_img = []
    for path in path_array:
        res_img.append(image_handler(path))
    return res_img


def handle_answer(answer):
    global current_index
    global reviews
    reviews[current_index] = answer
    print(f"answer for page {current_index + 1} is {answer}")


def good_review():
    global reviews
    reviews['rate'] = 'good'
    ending_page()


def next_question():
    global current_index
    if (current_index + 1) == len(questions):
        current_index = (current_index + 1) % len(questions)
        print("reaching ending page")
        reviews['rate'] = 'bad'
        ending_page()
    else:
        current_index = (current_index + 1) % len(questions)
        show_question(current_index)


def previous_question():
    global current_index
    current_index = (current_index - 1) % len(questions)
    show_question(current_index)


def destroy_widget():
    for widget in questions_frame.winfo_children():
        widget.destroy()


# ----------------- object declaration
mouse = PyMouse()
keyboard = PyKeyboard()
rfg = RealtimeFirebaseGet()
rfu = RealtimeFirebaseUpload()

# ------------------ variable declaration
global up_list, period, img_hand_5_path, img_hand_4_path, img_path_array, intro_img
up_list = []
period = 10
img_hand_5_path = "./pictures/five.jpg"
img_hand_4_path = "./pictures/four.jpg"
img_hand_1_path = "./pictures/one.jpg"
img_path_array = ["./pictures/one.jpg", "./pictures/two.jpg", "./pictures/three.jpg"]
intro_img = Image.open("intro.png")

global ending_img, resized_ed_img
ending_img = Image.open("ending.png")
resized_ed_img = ending_img.resize((500, 430), Image.Resampling.LANCZOS)

global reviews
reviews = {}

# declaration
global current_index
current_index = 0

global questions
questions = rfg.get_data()

# Create the main window
window = tk.Tk()
window.bind('<Escape>', lambda e: window.quit())
window.geometry("1000x500")

questions_frame = tk.Frame(window, width=500, height=500, bg="red")
questions_frame.grid(row=0, column=0)
questions_frame.grid_propagate(False)

# Create the right frame
camera_frame = tk.Label(window, width=500, height=500, bg="blue")
camera_frame.grid(row=0, column=1)
camera_frame.grid_propagate(False)

# Open the camera
cap = cv2.VideoCapture(3)

video_queue = queue.Queue()
hand_count_queue = queue.Queue()

video_thread = threading.Thread(target=display_video)
processing_thread = threading.Thread(target=process_frame)
capture_thread = threading.Thread(target=video_capture)
questions_thread = threading.Thread(target=landing_page)

video_thread.start()
processing_thread.start()
capture_thread.start()
questions_thread.start()

window.mainloop()
cap.release()
cv2.destroyAllWindows()
