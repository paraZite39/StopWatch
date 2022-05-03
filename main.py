from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import sys
import time


class StopWatch:
    def __init__(self, root):
        """
        Initializes stopwatch
        :param root: tk root in which to put the elements
        """
        self.after_id = None
        self.running = False
        self.seconds = 0
        self.stopwatch_label = tk.Label(root, text='00:00:00', font=('Helvetica', 48))
        self.stopwatch_label.pack()

        # main stopwatch buttons - start, pause, reset, quit
        self.start_button = tk.Button(root, text='start', height=3, width=7, bg='#567', fg='White',
                                      font=('Arial', 20), command=self.start)
        self.start_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(root, text='pause', height=3, width=7, bg='#567', fg='White',
                                      font=('Arial', 20), command=self.pause)
        self.pause_button.pack(side=tk.LEFT)

        self.reset_button = tk.Button(root, text='reset', height=3, width=7, bg='#567', fg='White',
                                      font=('Arial', 20), command=self.reset)
        self.reset_button.pack(side=tk.LEFT)

        self.quit_button = tk.Button(root, text='save', height=3, width=7, bg='#567', fg='White',
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
        if not self.running:
            self.start_button.configure(state=tk.DISABLED)
            self.running = True
            print("STARTED")
            self.stopwatch_label.configure(text=self.get_label())
            self.after_id = self.stopwatch_label.after(1000, self.tick)

    def pause(self):
        if self.running:
            self.running = False
            self.start_button.configure(state=tk.ACTIVE)

    def reset(self):
        if self.running:
            self.running = False
            self.seconds = 0
            self.stopwatch_label.after_cancel(self.after_id)
            self.start()
        else:
            self.seconds = 0
            self.stopwatch_label.configure(text=self.get_label())

    def tick(self):
        if self.running:
            self.seconds += 1
            self.stopwatch_label.config(text=self.get_label())
            self.after_id = self.stopwatch_label.after(1000, self.tick)

    def save(self):
        if self.running:
            self.running = False
            print("Save...")
            category = simpledialog.askstring(title="Save Timer",
                                              prompt="What did you do during this time?")
            print(category)


class StopWatchHistory:
    def __init__(self, root):
        self.history = []
        self.index = 1
        self.hist_gui = tk.Listbox(root, width=30)
        self.hist_gui.pack(side=tk.LEFT)

    def add_record(self, record):
        self.hist_gui.insert(self.index, record)
        self.index += 1


root = tk.Tk()
root.geometry('470x235')
root.title('Stopwatch')
tabControl = ttk.Notebook(root)

tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

tabControl.add(tab1, text='Stopwatch')
tabControl.add(tab2, text='History')
tabControl.pack(expand=1, fill='both' )

s = StopWatch(tab1)
h = StopWatchHistory(tab2)

h.add_record(['03/05/22 Editing 00:53:01'])

root.mainloop()
