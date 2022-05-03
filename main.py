from datetime import datetime
from datetime import date
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import sys
import time


class StopWatch:
    def __init__(self, watch_root, hist):
        """
        Initializes stopwatch
        :param root: tk root in which to put the elements
        :param hist: stopwatch history in which to store records
        """
        self.hist = hist

        # id for recursive tick function
        self.after_id = None

        self.running = False
        self.seconds = 0
        self.stopwatch_label = tk.Label(watch_root, text='00:00:00', font=('Helvetica', 48))
        self.stopwatch_label.pack()

        # main stopwatch buttons - start, pause, reset, quit
        self.start_button = tk.Button(watch_root, text='start', height=3, width=7, bg='#567', fg='White',
                                      font=('Arial', 20), command=self.start)
        self.start_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(watch_root, text='pause', height=3, width=7, bg='#567', fg='White',
                                      font=('Arial', 20), command=self.pause)
        self.pause_button.pack(side=tk.LEFT)

        self.reset_button = tk.Button(watch_root, text='reset', height=3, width=7, bg='#567', fg='White',
                                      font=('Arial', 20), command=self.reset)
        self.reset_button.pack(side=tk.LEFT)

        self.quit_button = tk.Button(watch_root, text='save', height=3, width=7, bg='#567', fg='White',
                                     font=('Arial', 20), command=self.save)
        self.quit_button.pack(side=tk.LEFT)

    def get_label(self):
        """
        Returns a string representation of the current number of seconds
        :return: stopwatch label
        """
        s = self.seconds
        h = s // 3600
        s -= (h * 3600)
        m = s // 60
        s -= (m * 60)

        return f'{round(h):02}:{round(m):02}:{round(s):02}'

    def start(self):
        """
        Starts the stopwatch. Works only if stopwatch is not running
        """
        if not self.running:
            self.start_button.configure(state=tk.DISABLED)
            self.running = True

            # set stopwatch label to current time, make it call tick function after a second
            self.stopwatch_label.configure(text=self.get_label())
            self.after_id = self.stopwatch_label.after(1000, self.tick)

    def pause(self):
        """
        Pauses the stopwatch. Works only if stopwatch is running
        """
        if self.running:
            self.running = False
            self.start_button.configure(state=tk.ACTIVE)

    def reset(self):
        """
        Resets the stopwatch's second counter to 0, starts over if stopwatch is running
        """
        if self.running:
            self.running = False
            self.seconds = 0

            # cancels call to tick function
            self.stopwatch_label.after_cancel(self.after_id)
            self.start()
        else:
            self.seconds = 0
            self.stopwatch_label.configure(text=self.get_label())

    def tick(self):
        """
        Recursively ticks stopwatch every second (increments second counter, updates label)
        Should not be called directly, as it is only called by the start function
        """
        if self.running:
            self.seconds += 1
            self.stopwatch_label.config(text=self.get_label())

            # calls function again after one second
            self.after_id = self.stopwatch_label.after(1000, self.tick)

    def save(self):
        """
        Saves current timer (prompts for category) and resets
        """
        if self.running:
            self.running = False

        print("Saving...")
        category = simpledialog.askstring(title="Save Timer",
                                          prompt="What did you do during this time?")

        # adds record with today's date, current timer and provided category
        self.hist.add_record(date.today().strftime("%d/%m/%Y") + " | " + self.get_label() + " | " + category)
        self.start_button.configure(state=tk.ACTIVE)
        self.reset()


class StopWatchHistory:
    def __init__(self, hist_root):
        self.history = []
        self.index = 1
        self.hist_gui = tk.Listbox(hist_root, width=30)
        self.hist_gui.pack(side=tk.LEFT)

    def add_record(self, record):
        self.hist_gui.insert(self.index, record)
        self.index += 1


class MainApp:
    def __init__(self, main_root):
        self.tab_control = ttk.Notebook(main_root)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab1, text='Stopwatch')
        self.tab_control.add(self.tab2, text='History')
        self.tab_control.pack()

        self.history = StopWatchHistory(self.tab2)
        self.stopwatch = StopWatch(self.tab1, self.history)


root = tk.Tk()
root.geometry('486x220')
root.title('Stopwatch')

app = MainApp(root)
root.mainloop()
