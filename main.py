import tkinter as tk
from tkinter import ttk
import random
import sqlite3 as sq
from playsound import playsound
import sys


DB_NAME = "undefined"
EVAL_LTRS = {
    None: "#ffdd7d",  # init colour for qwerty keyboard
    0: "#d44c4c",     # letter not found in word
    1: "#4ed433",     # letter found at correct pos
    2: "#ffe505"      # letter found at incorrect pos
}
QWERTY = "QWERTYUIOPASDFGHJKLZXCVBNM⏎␡"
FNT = 'consolas'
BLD = 'bold'
MAIN_BG = "#63AFDD"
BTN_COL = "#ADE0FF"
BTN_FG = "#2A485B"
HILITE = "#81BFE5"
TXT_COL = "#0F2A3B"
GREEN = "#6edb7a"
RED = "#bf695a"

# ------------------------------------------------------------
# GLOBALS
w_num = 0
guesses = ["     ", "     ", "     ", "     ", "     ", "     "]
found = []
play = False
passage = []
turn = 0
words_typed_successfully = 0
words_typed_total = 0
accuracy = "0.00%"
WPM = 0
m = 0
s = 0


def get_words():
    global passage
    passage = []
    with open('words.txt', 'r') as file:
        long_txt = file.read()
    FULL_WORD_ARRAY = long_txt.split()
    random.shuffle(FULL_WORD_ARRAY)
    for i in range(len(FULL_WORD_ARRAY)+1):
        passage.append(FULL_WORD_ARRAY[len(FULL_WORD_ARRAY)-1 - i])


def clock():
    global s, m, words_typed_successfully
    if len(str(m)) < 2:
        min_string = '0' + str(m)
    else:
        min_string = str(m)
    if len(str(int(s))) < 2:
        sec_string = '0' + str(int(s))
    else:
        sec_string = str(int(s))
    if s >= 59.8:
        s = 0
        m = m+1
        if len(str(m)) < 2:
            min_string = '0' + str(m)
        else:
            min_string = str(m)
    else:
        s = s + 0.2
    time_mins_secs = min_string  + " : " + sec_string

    time_str.set(time_mins_secs)
    words_per_min = str((words_typed_successfully / ((m * 60) + s)) * 60)
    if len(words_per_min) > 4:
        words_per_min = words_per_min[0:4]

    string = "Words: " + str(words_typed_successfully) + "    WPM: " + words_per_min + "    Accuracy: " + accuracy
    comb_var.set(string)
    if play is True:
        app.after(200, clock)


def draw_road(self, btn_frame):
    global passage, w_num
    if btn_frame is not None:
        for button in btn_frame.winfo_children():
            button.destroy()
    w_len = 15
    rows = 15
    f_size = 3
    try:
        w_num = w_num - (rows + 1)
    except:
        pass
    self.rw = [0 for x in range(rows)]
    self.lbl = [0 for x in range(rows)]

    for x in range(rows):
        self.rw[x] = tk.LabelFrame(btn_frame, bg=MAIN_BG, bd=0)
        self.rw[x].pack()
    for x in range(rows):
        if x > 0:
            try:
                word = passage[w_num]
            except:
                word = " "
            spaces = w_len - len(word)
            word = (int((spaces/2)) * '-') + ' ' + word + ' ' + (int((spaces/2))*'-')
        else:
            word = '.......' + (x*5)*'.'
        self.lbl[x] = tk.Label(self.rw[x], text=word, font=(FNT, f_size, BLD),
                               bg=MAIN_BG, fg=TXT_COL, width=20)
        self.lbl[x].pack()
        f_size = f_size + int((2*x)/4)
        w_num = w_num + 1
    print(passage[w_num])
    return passage[w_num]


def reset(self, btn_frame):
    global turn, words_typed_successfully, words_typed_total, m, s, play, w_num, accuracy
    w_num = 0
    get_words()
    play = False
    turn = 1
    words_typed_successfully = 0
    words_typed_total = 0
    m = 0
    s = 0
    accuracy = "0.00%"
    draw_road(self, btn_frame)
    #comb_var.set("Words: 0    WPM: 0.0    Accuracy: 0.00%")


def logic(self, btn_frame):
    global turn, words_typed_successfully, words_typed_total, accuracy, play
    if turn == 1:
        play = True
        clock()
    typed_word = app.entry.get().strip() # store entry box as variable
    word = draw_road(self, btn_frame)
    app.entry.delete(0, tk.END)
    if turn > 0:
        if word == typed_word:
            playsound("good.mp3", False)
            app.entry.config(bg=GREEN)
            words_typed_successfully = words_typed_successfully + 1
            words_typed_total = words_typed_total + 1
        else:
            if turn != 0:
                playsound("bad.mp3", False)
                app.entry.config(bg=RED)
                words_typed_total = words_typed_total + 1

    if words_typed_total != 0:
        acc = str((words_typed_successfully / words_typed_total) * 100)
        if len(acc) > 5:
            acc = acc[0:5]
        accuracy = acc + '%'

    turn = turn+1


def sql_query(query, return_records=False):
    """ Run SQL query, with the option to return the results to the calling code as a list. """
    connection = sq.connect(DB_NAME)  # create/connect to db
    cursor = connection.cursor()  # create a cursor object
    cursor.execute(query)
    records = cursor.fetchall()
    connection.commit()  # commit to database
    connection.close()  # close connection to database
    if return_records:
        return records


def entry_ctrl_bs(event):
    ent = event.widget
    end_idx = ent.index(tk.INSERT)
    start_idx = ent.get().rfind(" ", None, end_idx)
    ent.selection_range(start_idx, end_idx)

def space(event):
    ent = event.widget
    end_idx = ent.index(tk.INSERT)
    start_idx = ent.get().rfind(" ", None, end_idx)
    ent.selection_range(start_idx, end_idx)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('TYPE RACER')
        self.geometry("740x900")
        try:
            self.iconbitmap("car.ico")
        except:
            pass
        self.configure(bg=MAIN_BG)
        self.style = ttk.Style()  # add styling
        self.style.theme_use('default')  # add theme
        title = tk.LabelFrame(self, bg=MAIN_BG, padx=20, pady=0, bd=0)
        title.pack()
        title_text = tk.Label(title, text="🚔", font=(FNT, 24, 'bold'), bg=MAIN_BG, fg=TXT_COL)
        title_text.grid(row=1, column=1)
        type_racer = tk.LabelFrame(self, bg=MAIN_BG, padx=0, pady=0, bd=3)
        type_racer.pack()




if __name__ == "__main__":
    app = App()
    get_words()
    playsound("start.mp3", False)
    button_frame = tk.LabelFrame(app, bd=0, bg=MAIN_BG)
    button_frame.pack(pady=0)
    entry_frame = tk.LabelFrame(app, bg=MAIN_BG, bd=0)
    entry_frame.pack()
    app.entry = tk.Entry(entry_frame, bg=HILITE, font=(FNT, 60, BLD), width=15, justify=tk.CENTER, bd=8)
    app.entry.pack(padx=10, pady=20)
    cmd_btn_frame = tk.LabelFrame(app, bd=0, bg=MAIN_BG)
    cmd_btn_frame.pack()
    app.entry.focus()
    timer_frame = tk.LabelFrame(app, bg=MAIN_BG, bd=0)
    timer_frame.pack(pady=0)
    time_str = tk.StringVar()

    comb_var = tk.StringVar()
    tk.Label(timer_frame, textvariable=comb_var, width=60, bd=5, font=(FNT, 18, BLD), bg=MAIN_BG).pack()
    comb_var.set("Words: 0    WPM: 0.0    Accuracy: 0.00%")

    tk.Button(timer_frame, textvariable=time_str, width=30, bd=5, height=2, font=(FNT, 90, BLD), bg=HILITE).pack(pady=30, padx=30)
    time_str.set('00 : 00')

    reset_btn = tk.Button(app, text="Reset", width=6, bd=3, font=(FNT, 16, BLD), bg=HILITE,
                          command=lambda: reset(app, button_frame)).place(relx=.01, rely=.01)
    score_btn = tk.Button(app, text="Scores", width=6, bd=3, font=(FNT, 16, BLD), bg=HILITE).place(relx=.01, rely=.07)

    logic(app, button_frame)

    app.entry.bind('<Return>', lambda x=None: logic(app, button_frame))
    app.entry.bind('<space>', lambda x=None: logic(app, button_frame))
    app.entry.bind('<Control-BackSpace>', entry_ctrl_bs)
    app.mainloop()