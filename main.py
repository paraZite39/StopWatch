from datetime import date
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import filedialog
from PIL import ImageTk, Image
import glob
import random


class LabelDialog:
    def __init__(self, popup_root, categories):
        """
        Creates a custom pop-up that prompts for the timer label and category
        :param popup_root: the pop-up parent
        :param categories: list of label categories (ex. work, study...)
        """
        top = self.top = tk.Toplevel(popup_root)
        self.final_label = None
        self.final_category = None
        self.canceled = False

        # prompt for label
        self.label = tk.Label(top, text="What did you do during this time? (10 chars max)")
        self.label.grid(row=0, padx=10, pady=10)

        self.myEntryBox = tk.Entry(top)
        self.myEntryBox.grid(row=0, column=1, padx=10, pady=10)
        self.myEntryBox.focus()

        # prompt for category
        self.cat_label = tk.Label(top, text="What category does this label go into?")
        self.cat_label.grid(row=1, column=0)

        self.cat_input = tk.StringVar()
        self.category_combo = ttk.Combobox(top, textvariable=self.cat_input, values=categories)
        self.category_combo.grid(row=1, column=1, padx=10)

        # focus combobox on first item
        self.category_combo.current(0)

        # submit button
        self.mySubmitButton = tk.Button(top, text='Submit', command=self.send)
        self.mySubmitButton.grid(row=2, column=0, padx=10, pady=10)

        self.top.protocol("WM_DELETE_WINDOW", self.on_closing)

    def send(self):
        """
        Submit button pressed, set final label and category values and destroy pop-up
        """
        self.final_label = self.myEntryBox.get()
        self.final_category = self.cat_input.get()
        self.top.destroy()

    def on_closing(self):
        sure = messagebox.askyesno(title="Cancelling label",
                                   message="Are you sure you want to cancel? Record will not be saved.")
        print(sure)
        if sure:
            self.canceled = True
            self.top.destroy()


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
        self.photo_frame = tk.Label(self.root, image=self.init_photo)
        self.photo_frame.pack(pady=10)

        # id for recursive tick function
        self.after_id = None

        self.running = False
        self.seconds = 0
        self.stopwatch_label = tk.Label(watch_root, text=self.get_label(), font=('Helvetica', 48))
        self.stopwatch_label.pack()

        # main stopwatch buttons - start, pause, reset, quit
        self.button_frame = tk.Frame(watch_root)
        self.start_button = tk.Button(self.button_frame, text='start', height=2, width=9, bg='#567', fg='White',
                                      font=('Arial', 20), command=self.start)
        self.start_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(self.button_frame, text='pause', height=2, width=9, bg='#567', fg='White',
                                      font=('Arial', 20), command=self.pause)
        self.pause_button.pack(side=tk.LEFT)

        self.reset_button = tk.Button(self.button_frame, text='reset', height=2, width=9,bg='#567', fg='White',
                                      font=('Arial', 20), command=self.reset)
        self.reset_button.pack(side=tk.LEFT)

        self.quit_button = tk.Button(self.button_frame, text='save', height=2, width=9, bg='#567', fg='White',
                                     font=('Arial', 20), command=self.save)
        self.quit_button.pack(side=tk.LEFT)
        self.button_frame.pack()

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
        print(new_img)
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
        print(event, event.keycode)
        if event.keycode == 32: # space pressed
            print('space')
            if self.running:
                self.running = False
                self.pause()
            else:
                self.running = True
                self.start()
        elif event.keycode == 27:
            print('esc')
            sure = messagebox.askyesno(title="Reset", message="Are you sure you want to reset?")
            if sure:
                self.reset()


class PomodoroTimer(StopWatch):
    def __init__(self, timer_root, photos):
        """
        Initializes pomodoro timer
        :param timer_root: tk root in which to put the elements
        """
        super().__init__(timer_root, None, photos)
        self.is_focused = True
        self.focus_count = 0
        self.break_count = 0
        self.focus_string = tk.StringVar(value=str(self.focus_count))
        self.break_string = tk.StringVar(value=str(self.break_count))

        self.focus_label = tk.Label(timer_root, text='Focus count: ' + str(self.focus_count))
        self.break_label = tk.Label(timer_root, text='Break count: ' + str(self.break_string))
        self.focus_label.pack()
        self.break_label.pack()

        self.seconds = 1500
        self.update_label()

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
        if self.is_focused:
            self.is_focused = False
            self.focus_count += 1
            self.reset(300)
            if start_break := messagebox.askyesno(title="Focus done",
                                                  message="Great work! Would you like to start the break now?"):
                self.start()
            else:
                self.pause()

        else:
            self.is_focused = True
            self.break_count += 1
            self.reset(1500)
            if start_focus := messagebox.askyesno(title="Break done",
                                                  message="Break over! Would you like to start working now?"):
                self.start()
            else:
                self.pause()


class StopWatchHistory:
    def __init__(self, hist_root, photos):
        """
        Initializes stopwatch history
        When application is started, it will search for file 'history.txt'
        :param hist_root: the root in which to show the history
        """
        self.hist_root = hist_root
        self.history_categories = {'Work': [], 'Study': [], 'Exercise': [], 'Other': []}
        self.index = 1
        self.photos = photos

        # tree for displaying records
        self.hist_gui = ttk.Treeview(hist_root)
        self.hist_gui['columns'] = ("Date", "Length", "Label")
        self.hist_gui.column("#0", width=75, minwidth=25)
        self.hist_gui.column("Date", anchor=tk.W, width=70)
        self.hist_gui.column("Length", anchor=tk.CENTER, width=60)
        self.hist_gui.column("Label", anchor=tk.W, width=100)

        self.hist_gui.heading("#0", text="Category", anchor=tk.W)
        self.hist_gui.heading("Date", text="Date", anchor=tk.W)
        self.hist_gui.heading("Length", text="Length", anchor=tk.CENTER)
        self.hist_gui.heading("Label", text="Label", anchor=tk.W)

        self.hist_gui.pack(side=tk.LEFT, padx=5, pady=5)

        self.init_tree()

        # frame on the right side (details)
        self.f = tk.Frame(hist_root, height=350)
        self.f.pack(side=tk.LEFT, padx=10, pady=20)
        self.title_lab = tk.Label(self.f, text='', font=('Arial', 12))
        self.title_lab.pack(anchor='w')
        self.date_lab = tk.Label(self.f, text='', font=('Arial', 10))
        self.date_lab.pack(anchor='w')
        self.length_lab = tk.Label(self.f, text='', font=('Arial', 10))
        self.length_lab.pack(anchor='w')

        # frame for buttons (delete, load, save)
        self.button_frame = tk.Frame(self.f, pady=5)
        self.button_frame.pack(side=tk.BOTTOM)
        self.delete_button = tk.Button(self.button_frame, text='Delete')
        self.delete_button.pack(side=tk.LEFT)
        self.delete_button.configure(state=tk.DISABLED)

        self.load_button = tk.Button(self.button_frame, text='Load', command=self.load_records)
        self.load_button.pack(side=tk.LEFT)
        self.save_button = tk.Button(self.button_frame, text='Save', command=self.save_records)
        self.save_button.pack(side=tk.LEFT)

        # respond to click on the treeview
        self.hist_gui.bind("<ButtonRelease-1>", self.onselect)

        # automatically load records from history.txt
        try:
            self.load_records('history.txt')
        except FileNotFoundError:
            print("History file not found...")
            pass

    def init_tree(self):
        """
        Takes categories from the 'history_categories' dict and inserts them in treeview
        """
        for ind, cat in enumerate(self.history_categories.keys()):
            self.hist_gui.insert(parent='', index='end', iid=cat, text=cat, values=())

    def onselect(self, _):
        """
        Update the right frame when a record from tree is selected
        :param _: event parameter, not used
        """
        date, length, label = None, None, None

        # take selected treeview item
        selection = self.hist_gui.focus()

        if not selection:
            return

        # take selected item's parent (category)
        category = self.hist_gui.parent(selection)
        # take selected item's values (date, length, label)
        vals = self.hist_gui.item(selection, 'values')

        # no record is selected => return
        if not vals:
            return

        if len(vals) == 3:
            date, length, label = vals

        # update labels with record data
        self.title_lab.configure(text='Label: ' + (label or 'null'))
        self.date_lab.configure(text='Date: ' + (date or 'null'))
        self.length_lab.configure(text='Length: ' + (length or 'null'))

        # activate delete button
        self.delete_button.configure(state=tk.ACTIVE,
                                     command=lambda: self.delete_record(selection, ' | '.join(vals), category))

    def add_record(self, record, category):
        """
        Enters record into the history
        :param record: the record to be introduced
        :param category: the label's category
        """
        date, length, label = record.split(' | ')
        if not self.is_duplicate(record, category):
            # add record to category dict
            self.history_categories[category] = self.history_categories.get(category, []) + [record]
            # add record to treeview
            self.hist_gui.insert(parent=category, index=self.index, text="", values=(date, length, label))
            self.index += 1
        else:
            messagebox.showerror(title="Duplicate label", message="Duplicate label, please try again.")
            new_record, new_label = None, ''
            # if label is empty, duplicate or too long
            while (not new_record or not new_label
                   or self.is_duplicate(new_record, category) or len(new_label) > 10):
                new_label = simpledialog.askstring("New label", prompt="Please enter new label:")
                new_record = ' | '.join([date, length, new_label or 'default'])

            self.add_record(new_record, category)

    def delete_record(self, ind, label, category):
        """
        Delete record from treeview
        :param category: record's category
        :param ind: record's index
        :param label: record to be deleted
        """
        # delete record from treeview (with index)
        self.hist_gui.delete(ind)
        # delete record from category dict
        self.history_categories[category].remove(label)

        self.reset_labels()

        if self.hist_gui.size() == 0:
            self.delete_button.configure(state=tk.DISABLED)

    def reset_labels(self):
        """
        Reset labels to their initial state (empty)
        """
        self.date_lab.configure(text='')
        self.title_lab.configure(text='')
        self.length_lab.configure(text='')

    def load_records(self, filename=None):
        """
        Fetch history records from a given file
        :param filename(optional) - filename from which to load records
        """
        def is_valid(line):
            """
            Check if record line is valid (date, timer and label)
            :param line: line to be checked
            :return: True if record is valid, False otherwise
            """

            import re

            elements = line.split(' | ')
            if len(elements) == 3:
                # record contains a date of format dd/mm/yyyy
                valid_date = re.match(r"^\d{2}/\d{2}/\d{4}$", elements[0])
                # record contains a timer of format hh:mm:ss
                valid_time = re.match(r"^\d{2}:\d{2}:\d{2}$", elements[1])
                # record contains a label (between 1 and 10 characters)
                valid_label = re.match(r"^.{1,10}$", elements[2])

                if valid_date and valid_time and valid_label:
                    return True

            return False

        if not filename:
            # start load by asking for filename
            filename = filedialog.askopenfilename(title="Open file",
                                                  filetypes=(("Text files", '*.txt'),
                                                             ("All files", "*.*")),
                                                  initialfile="history.txt")

        # cancel pressed
        if not filename:
            return

        try:
            with open(filename, 'r') as f:
                # invalid file = no usable records / all duplicates
                invalid_file = True
                for record in f:
                    record = record.strip('\n')
                    # label and category, split by tab '\t'
                    if len(record.split('\t')) == 2:
                        label, category = record.split('\t')
                        # if record respects format defined at the start of this function,
                        # isn't duplicate and category is valid
                        if is_valid(label) and not self.is_duplicate(label, category) \
                                and category in self.history_categories.keys():
                            # file isn't invalid, as a record was found
                            invalid_file = False
                            self.add_record(label, category)

                # no valid records found in file
                if invalid_file:
                    messagebox.showerror(title="Error", message="No useful records found on file.")

        except FileNotFoundError:
            messagebox.showerror(title="Error", message="File not found.")
            # call function again
            self.load_records()

    def save_records(self):
        """
        Save records to a given filename
        """
        # no records to save
        if self.hist_gui.size() == 0:
            messagebox.showerror(title="Error", message="Cannot save empty list.")
            return

        # prompt for filename
        filename = filedialog.asksaveasfilename(title="Save file",
                                                filetypes=(('Text files', '*.txt'),
                                                           ('All files', '*.*')),
                                                defaultextension=".txt",
                                                initialfile="history.txt")

        # cancel pressed
        if not filename:
            return

        try:
            with open(filename, 'w') as f:
                # iterate through records in list box, writing them to file
                for category in self.history_categories:
                    records = self.history_categories[category]
                    for line in records:
                        write_line = line + "\t" + category + "\n"
                        f.write(write_line)
        except FileNotFoundError:
            messagebox.showerror(title="Error", message="File not found.")
            # call function again
            self.save_records()

    def is_duplicate(self, record, category):
        """
        Given a certain record, iterates through existing list to see if it's a duplicate
        :param record: the record to be checked for duplicates
        :param category: the record's category
        :return: True if record is a duplicate, False otherwise
        """
        records = self.history_categories[category]
        if record in records:
            return True

        return False


class MainApp:
    def __init__(self, main_root):
        """
        Initializes main stopwatch app
        :param main_root: the root in which to display the app
        """
        self.root = main_root
        self.photos = {}
        self.photo_categories = ['work', 'break', 'exercise', 'other']
        for cat in self.photo_categories:
            self.photos[cat] = glob.glob(f'super_secret_pictures/{cat}_*.*')
        print(self.photos)

        # two tabs - stopwatch and history
        self.tab_control = ttk.Notebook(main_root)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab3 = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab1, text='Stopwatch')
        self.tab_control.add(self.tab2, text='History')
        self.tab_control.add(self.tab3, text='Pomodoro')
        self.tab_control.pack()

        self.history = StopWatchHistory(self.tab2, self.photos)
        self.stopwatch = StopWatch(self.tab1, self.history, self.photos)
        self.pomodoro = PomodoroTimer(self.tab3, self.photos)

        main_root.protocol("WM_DELETE_WINDOW", self.close_app)
        self.root.bind("<Key>", lambda event: self.key_press(event))

    def key_press(self, event):
        print(event)
        print(self.tab_control.select())

    def close_app(self):
        """
        Called when the user presses the 'X' button. Asks confirmation for closing and saving records
        """
        sure_close = messagebox.askyesno(title="Close", message="Are you sure you want to close this application?")
        if sure_close:
            save = messagebox.askyesno(title="Save", message="Would you like to save your records?")
            if save:
                self.history.save_records()

            self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Stopwatch')
    root.resizable(False, False)

    app = MainApp(root)
    root.mainloop()
