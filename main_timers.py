import random
import tkinter as tk
from datetime import date
from tkinter import messagebox
from PIL import ImageTk, Image
from dialog_boxes import LabelDialog


class StopWatch:
    def __init__(self, watch_root, hist, photos):
        """
        Initializes stopwatch
        :param watch_root: tk root in which to put the elements
        :param hist: stopwatch history in which to store records
        :param photos: dict with pictures separated by categories
        """
        self.hist = hist
        self.root = watch_root
        self.photos = photos
        self.init_photo = self.get_photo('break')
        self.photo_frame = tk.Label(watch_root, image=self.init_photo)
        self.photo_frame.grid(row=0, column=0, columnspan=2)

        # id for recursive tick function
        self.after_id = None

        self.running = False
        self.seconds = 0
        self.stopwatch_label = tk.Label(watch_root, text=self.get_label(), font=('Helvetica', 48))
        self.stopwatch_label.grid(row=1, column=0, columnspan=2)

        # main stopwatch buttons - start, pause, reset, quit
        self.start_button = tk.Button(watch_root, text='start', height=2, width=9, bg='#567', fg='White',
                                      font=('Arial', 20), command=self.start)
        self.start_button.grid(row=3, column=0)

        self.pause_button = tk.Button(watch_root, text='pause', height=2, width=9, bg='#567', fg='White',
                                      font=('Arial', 20), command=self.pause)
        self.pause_button.grid(row=3, column=1)

        self.reset_button = tk.Button(watch_root, text='reset', height=2, width=9, bg='#567', fg='White',
                                      font=('Arial', 20), command=self.reset)
        self.reset_button.grid(row=4, column=0)

        self.quit_button = tk.Button(watch_root, text='save', height=2, width=9, bg='#567', fg='White',
                                     font=('Arial', 20), command=self.save)
        self.quit_button.grid(row=4, column=1)

        self.root.bind("<Key>", self.key_pressed)

    def get_photo(self, cat):
        """
        Returns a random photo, given a category
        :param cat: (no pun intended) category from which to pick photo
        :return: photo
        """

        random_img = Image.open(random.choice(self.photos[cat]))
        return ImageTk.PhotoImage(random_img.resize((225, 175)))

    def get_label(self):
        """
        Returns a string representation of the current number of seconds
        :return: stopwatch label
        """
        s = self.seconds
        # get number of hours (1h = 3600 seconds), subtract from counter
        h = s // 3600
        s -= (h * 3600)
        # get number of minutes (1m = 60 seconds), subtract from counter
        m = s // 60
        s -= (m * 60)

        # format as hh:mm:ss
        return f'{round(h):02}:{round(m):02}:{round(s):02}'

    def update_label(self):
        self.stopwatch_label.configure(text=self.get_label())

    def update_photo(self, cat):
        new_img = self.get_photo(cat)
        self.photo_frame.configure(image=new_img)
        self.photo_frame.image = new_img

    def start(self):
        """
        Starts the stopwatch. Works only if stopwatch is not running
        """
        if not self.running:
            self.start_button.configure(state=tk.DISABLED)
            self.running = True

            # set stopwatch label to current time, make it call tick function after a second
            self.update_label()
            self.update_photo('work')
            self.after_id = self.stopwatch_label.after(1000, self.tick)

    def pause(self):
        """
        Pauses the stopwatch. Works only if stopwatch is running
        """
        if self.running:
            self.running = False
            self.update_photo('break')
            self.start_button.configure(state=tk.ACTIVE)

    def reset(self, init_value=0):
        """
        Resets the stopwatch's second counter to 0, starts over if stopwatch is running
        :param init_value (optional) - the number of seconds to reset to
        """
        if self.running:
            self.running = False
            self.seconds = init_value

            # cancels call to tick function
            self.stopwatch_label.after_cancel(self.after_id)
            self.start()
        else:
            self.seconds = init_value
            self.update_label()

    def tick(self):
        """
        Recursively ticks stopwatch every second (increments second counter, updates label)
        Should not be called directly, as it is only called by the start function
        """
        if self.running:
            self.seconds += 1
            self.update_label()

            # calls function again after one second
            self.after_id = self.stopwatch_label.after(1000, self.tick)

    def save(self):
        """
        Saves current timer (prompts for category) and resets
        """
        # no seconds elapsed
        if self.seconds == 0:
            messagebox.showerror(title="Empty Save", message="Cannot save record of 0 seconds!")
            return

        # stop if running
        if self.running:
            self.running = False

        # prompt user for label and category
        category_values = self.hist.history_categories.keys()
        res = LabelDialog(self.root, tuple(category_values))
        self.root.wait_window(res.top)  # wait for prompt to be answered

        if not res.canceled:
            lab = res.final_label
        else:
            self.start_button.configure(state=tk.ACTIVE)
            return

        # label must be between 1 and 10 chars
        while 0 >= len(lab) or len(lab) > 10:
            res = LabelDialog(self.root, tuple(category_values))

        final_label = res.final_label
        final_category = res.final_category

        # adds record with today's date, current timer and provided category
        formatted_label = " | ".join([date.today().strftime("%d/%m/%Y"), self.get_label(), final_label])
        self.hist.add_record(formatted_label, final_category)
        self.start_button.configure(state=tk.ACTIVE)
        self.reset()

    def key_pressed(self, event):
        if event.keycode == 32:  # space pressed
            if self.running:
                self.running = False
                self.pause()
            else:
                self.running = True
                self.start()
        elif event.keycode == 27:
            sure = messagebox.askyesno(title="Reset", message="Are you sure you want to reset?")
            if sure:
                self.reset()


class PomodoroTimer(StopWatch):
    def __init__(self, timer_root, pomodoro_hist, photos):
        """
        Initializes pomodoro timer
        :param timer_root: tk root in which to put the elements
        """
        super().__init__(timer_root, pomodoro_hist, photos)
        self.pomodoro_hist = pomodoro_hist
        self.is_focused = True
        self.focus_count = 0
        self.break_count = 0

        self.focus_label = tk.Label(timer_root,
                                    text="Focus count: " + str(self.focus_count))
        self.break_label = tk.Label(timer_root,
                                    text="Break count: " + str(self.break_count))
        self.focus_label.grid(row=2, column=0)
        self.break_label.grid(row=2, column=1)

        self.seconds = 1500
        self.update_label()

        self.photo_frame.configure(bg="red")

    def tick(self):
        """
        Recursively ticks stopwatch every second (decrements second counter, updates label)
        Should not be called directly, as it is only called by the start function
        """
        if self.running:
            self.seconds -= 1
            self.update_label()

            if self.seconds <= 0:
                self.timer_done()
                return

            # calls function again after one second
            self.after_id = self.stopwatch_label.after(1000, self.tick)

    def timer_done(self):
        """
        When second counter hits 0, this function is called to switch from focus to break or vice-versa.
        """
        record_label = "Break"
        if self.is_focused:
            record_label = "Focus"
            self.is_focused = False

            self.photo_frame.configure(bg="green")
            self.focus_count += 1

            self.reset(300)
            self.pause()
            start_break = messagebox.askyesno(title="Focus done",
                                              message="Great work! Would you like to start the break now?")
            if start_break:
                self.start()
                self.update_photo('break')

        else:
            self.is_focused = True
            self.photo_frame.configure(bg="red")
            self.break_count += 1
            self.reset(1500)
            self.pause()
            start_focus = messagebox.askyesno(title="Break done",
                                              message="Break over! Would you like to start working now?")
            if start_focus:
                self.start()

        self.update_pomodoro_labels()
        record_line = date.today().strftime("%d/%m/%Y") + " | " + record_label
        self.pomodoro_hist.add_record(record_line, None)

    def update_pomodoro_labels(self):
        self.focus_label.configure(text="Focus count: " + str(self.focus_count))
        self.break_label.configure(text="Break count: " + str(self.break_count))
