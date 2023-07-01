import tkinter as tk
import customtkinter
import cv2
import mediapipe as mp
from PIL import Image, ImageTk
from module import find_position
from collections import Counter
import time
from datetime import datetime, date
from pymouse import PyMouse
from pykeyboard import PyKeyboard
from covifs_db import Get, Upload


class PageNavigation:
    def __init__(self):

        self.idle_timer = 2000
        self.end_page_timer = 60
        self.end_page_timer_status = False
        self.up_list = []

        self.page = 0
        self.all_answer = {}
        self.count = 0
        self.hand_detector_counter = 0
        self.total_up = 0
        self.mod_up = 0
        self.temp_up = None
        self.final_up = 0
        self.end_page = False

        # pymouse settings
        self.m = PyMouse()
        self.k = PyKeyboard()

        # OpenCv Init
        self.cap = cv2.VideoCapture(2)
        self.mpDraw = mp.solutions.drawing_utils
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()

        self.FireGet = Get()
        self.FireUp = Upload()
        self.height = self.FireGet.height
        self.confirm_button = ["yes", "no"]
        self.intro_page_image_path = "intro_page.png"

        # def run_process(self):
        self.root_tk = tk.Tk()
        self.root_tk.resizable(width=False, height=False)
        self.root_tk.bind('<Escape>', lambda e: self.root_tk.quit())
        self.root_tk.title("CustomTkinter Test")

        # choices frame
        self.main_frame = tk.Frame(self.root_tk, highlightbackground='black', highlightthickness=2)
        self.main_frame.pack(side=tk.LEFT)
        self.main_frame.pack_propagate(False)
        self.main_frame.configure(height=500, width=500)

        # cam frame
        self.cam_frame = tk.Label(self.root_tk, compound=tk.CENTER, anchor=tk.CENTER, relief=tk.RAISED)
        self.cam_frame.pack(side=tk.LEFT)
        self.cam_frame.pack_propagate(False)
        self.cam_frame.configure(width=500, height=500)

        self.process_paging(0, "no", self.FireGet.height, 0, 0, False)
        self.root_tk.after(1, self.update)
        self.root_tk.mainloop()

    # ----------------------------------------choices frame--------------------------------------------
    def process_paging(self, a, confirm, height, choice, activate_status, idle_status):
        global photo
        global page_data
        global original

        def obtain_time():
            today = date.today()
            now = datetime.now()
            time_now = now.strftime("%H:%M:%S")
            date_today = today.strftime("%d:%m:%Y")

            self.all_answer["time"] = time_now
            self.all_answer["date"] = date_today

        def reset():
            self.process_paging(0, "no", self.FireGet.height, 0, 0, True)
            self.all_answer.clear()
            print(self.end_page)

        def display_choice():
            def create_button(variable_name, text_name, position):
                locals()[variable_name] = customtkinter.CTkButton(master=subframe, text=text_name, width=120, height=32,
                                                                  border_width=0, corner_radius=8, )
                locals()[variable_name].pack(side=getattr(tk, position))

            text = "Choose problems that were faced below"
            lb = tk.Label(self.main_frame, text=text, font=('Bold', 10))
            lb.pack()

            options_btn = {}
            i = 1
            for data in page_data[self.page - 1]:
                if data != 0:
                    options_btn[data] = customtkinter.CTkButton(master=self.main_frame,
                                                                text=data,
                                                                width=120,
                                                                height=32,
                                                                border_width=0,
                                                                corner_radius=8, )
                    options_btn[data].pack(pady=10)
                    self.root_tk.bind(str(i), lambda e, data1=data: self.display_confirmation_page(e, data1, height))
                else:
                    self.root_tk.unbind(str(i))
                i = i + 1

            subframe = tk.Frame(self.main_frame, bg="white", width=500, height=100)
            subframe.pack(side=tk.BOTTOM)

            create_button("next_button", "Next", "RIGHT")
            create_button("back_button", "Back", "LEFT")

        if confirm == "good":
            obtain_time()
            self.all_answer["rate"] = "good"
            self.FireUp.upload(self.all_answer)
            self.page = 0
            self.end_page = True
            print(self.all_answer)
            self.all_answer.clear()

        if idle_status:
            self.page = 0

        # next & back function
        if confirm == "next":
            if self.page < height:
                self.page = self.page + 1
                self.all_answer[self.page - 1] = 0
        elif confirm == "back":
            if self.page > 1:
                self.page = self.page - 1
                self.all_answer[self.page - 1] = 0

        self.count = 0
        self.delete_page()

        if activate_status > 0:
            self.page = self.page + 1

        if self.page > 0:
            if confirm == "yes":
                self.all_answer[self.page - 1] = choice
                self.page = self.page + 1
                if self.page > height:
                    obtain_time()
                    self.all_answer["rate"] = "bad"
                    self.FireUp.upload(self.all_answer)
                    self.page = 0
                    self.end_page = True
                    print(self.all_answer)
                    reset()

            display_choice()
            self.root_tk.bind('4', lambda e: self.process_paging(0, "back", self.FireGet.height, 0, 0, False))
            self.root_tk.bind('5', lambda e: self.process_paging(0, "next", self.FireGet.height, 0, 0, False))
            self.root_tk.bind('6', lambda e: self.process_paging(0, "no", self.FireGet.height, 0, 0, True))
            # self.root_tk.unbind('5')
        else:
            self.FireGet.reset()
            page_data = self.FireGet.get_data()
            if self.end_page:
                original = Image.open("ending.png")
                self.end_page = False
                self.end_page_timer_status = True
            else:
                original = Image.open("intro.png")
            resized = original.resize((500, 500), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(resized)
            label = tk.Label(self.main_frame, image=photo)
            label.pack(side="bottom", fill="both")

            for i in range(2, 4):
                self.root_tk.unbind(str(i))
            self.root_tk.bind("1", lambda e: self.process_paging(0, "good", self.FireGet.height, 0, 0, False))
            self.root_tk.bind("5", lambda e: self.process_paging(0, "no", self.FireGet.height, 0, 1, False))
            self.root_tk.bind('6', lambda e: self.process_paging(0, "no", self.FireGet.height, 0, 0, True))

    def delete_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def display_confirmation_page(self, a, data, height):
        self.delete_page()
        self.count = 0
        next_page_status = 0
        display_confirmation_page_frame = tk.Frame(self.main_frame)
        display_confirmation_page_frame.pack_propagate(False)
        display_confirmation_page_frame.configure(height=720, width=1280)

        text = "Chosen " + data + " Are u sure?"
        lb = tk.Label(display_confirmation_page_frame, text=text, font=('Bold', 10))
        lb.pack()
        display_confirmation_page_frame.pack()

        options_btn = {}
        i = 1
        for field in self.confirm_button:
            options_btn[field] = customtkinter.CTkButton(master=display_confirmation_page_frame,
                                                         text=field,
                                                         width=120,
                                                         height=32,
                                                         border_width=0,
                                                         corner_radius=8, )
            options_btn[field].pack(pady=10)
            if self.page > height:
                next_page_status = 1
            self.root_tk.bind(str(i),
                              lambda e, field1=field: self.process_paging(e, field1, height, data, next_page_status,
                                                                          False))
            i = i + 1
        self.root_tk.bind('4', lambda e: self.process_paging(0, "no", self.FireGet.height, 0, 0, True))

    # ----------------------------------------Cam frame--------------------------------------------
    def get_frame(self):
        ret, frame = self.cap.read()
        if ret:
            return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            return ret, None

    def clear_frame(self):
        for widgets in self.root_tk.winfo_children():
            widgets.destroy()

    def update(self):
        up = 0
        tip = [8, 12, 16, 20]
        exists = self.cam_frame.winfo_exists
        if exists == 1:
            self.clear_frame()
        ret, frame = self.get_frame()
        frame_resized = cv2.resize(frame, (640, 480))
        a = find_position(frame_resized)
        # b = findnameoflandmark(frame_resized)

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

        # if self.detection_status == "ready":
        #     self.temp_up = up
        # else:
        #     self.temp_up = None

        # font = cv2.FONT_HERSHEY_SIMPLEX
        # text = "ready"
        # textsize = cv2.getTextSize(text, font, 1, 2)[0]
        # textx = int(frame_resized.shape[1] - textsize[0]) / 2
        # texty = int(frame_resized.shape[0] - textsize[1])
        # org = (int(textx), int(texty))
        #
        # cv2.putText(
        #     frame_resized,
        #     text,
        #     org,
        #     font,
        #     1,
        #     (209, 80, 0, 255),
        #     2
        # )

        img = Image.fromarray(frame_resized)
        imgtk = ImageTk.PhotoImage(image=img)
        self.cam_frame.imgtk = imgtk
        self.cam_frame.configure(image=imgtk)

        if self.hand_detector_counter == 0:
            if up > 0:
                self.hand_detector_counter += 1
                print("detected")
                self.count = 0

        if 11 > self.hand_detector_counter > 0:
            self.up_list.append(up)
            self.hand_detector_counter += 1

        if self.hand_detector_counter == 11:
            self.final_up = max(self.up_list, key=self.up_list.count)
            self.up_list = []
            self.hand_detector_counter = 0
            print(self.final_up)

        if self.final_up > 0:
            if self.final_up == 1:
                self.k.press_key('1')
            elif self.final_up == 2:
                self.k.press_key('2')
            elif self.final_up == 3:
                self.k.press_key('3')
            elif self.final_up == 4:
                self.k.press_key('4')
            elif self.final_up == 5:
                self.k.press_key('5')
            self.final_up = 0
            time.sleep(1.5)

        self.count += 1
        if self.end_page_timer_status:
            timer = self.end_page_timer
        else:
            timer = self.idle_timer
        if self.count >= timer:
            self.k.press_key('6')
            self.end_page_timer_status = False
        # print(self.count)
        self.cam_frame.after(1, self.update)


PageNavigation()
