from datetime import date
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import filedialog


class StopWatch:
    def __init__(self, watch_root, hist):
        """
        Initializes stopwatch
        :param watch_root: tk root in which to put the elements
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
        if self.seconds == 0:
            messagebox.showerror(title="Empty Save", message="Cannot save record of 0 seconds!")
            return

        if self.running:
            self.running = False

        print("Saving...")
        category = simpledialog.askstring(title="Save Timer",
                                          prompt="What did you do during this time? (Max length 10 characters)")

        while 0 >= len(category) or len(category) > 10:
            category = simpledialog.askstring(title="Save Timer",
                                              prompt="Please enter a string shorter than 10 characters")

        # adds record with today's date, current timer and provided category
        self.hist.add_record(date.today().strftime("%d/%m/%Y") + " | " + self.get_label() + " | " + category)
        self.start_button.configure(state=tk.ACTIVE)
        self.reset()


class StopWatchHistory:
    def __init__(self, hist_root):
        """
        Initializes stopwatch history
        :param hist_root: the root in which to show the history
        """
        self.hist_root = hist_root
        self.history_categories = dict()
        self.index = 1
        self.hist_gui = tk.Listbox(hist_root, width=45)
        self.hist_gui.pack(side=tk.LEFT, padx=5, pady=5)

        # frame on the right side (details)
        self.f = tk.Frame(hist_root, height=350)
        self.f.pack(side=tk.LEFT, padx=10, pady=20)
        self.title_lab = tk.Label(self.f, text='', font=('Arial', 12))
        self.title_lab.pack(anchor='w')
        self.date_lab = tk.Label(self.f, text='', font=('Arial', 10))
        self.date_lab.pack(anchor='w')
        self.length_lab = tk.Label(self.f, text='', font=('Arial', 10))
        self.length_lab.pack(anchor='w')

        self.button_frame = tk.Frame(self.f, pady=5)
        self.button_frame.pack(side=tk.BOTTOM)
        self.delete_button = tk.Button(self.button_frame, text='Delete')
        self.delete_button.pack(side=tk.LEFT)
        self.delete_button.configure(state=tk.DISABLED)

        self.load_button = tk.Button(self.button_frame, text='Load', command=self.load_records)
        self.load_button.pack(side=tk.LEFT)
        self.save_button = tk.Button(self.button_frame, text='Save', command=self.save_records)
        self.save_button.pack(side=tk.LEFT)

        self.hist_gui.bind("<<ListboxSelect>>", self.onselect)

    def onselect(self, e):
        """
        Update the right frame when a record from listbox is selected
        :param e: selection event
        """
        w = e.widget

        # no record is selected => return
        if not w.curselection():
            return

        ind = int(w.curselection()[0])
        record = w.get(ind).split(' | ')

        # update labels with record data
        self.title_lab.configure(text='Category: ' + record[-1])
        self.date_lab.configure(text='Date: ' + record[0])
        self.length_lab.configure(text='Length: ' + record[1])

        # activate delete button
        self.delete_button.configure(state=tk.ACTIVE, command=lambda: self.delete_record(ind))

    def add_record(self, record):
        """
        Enters record into the history
        :param record: the record to be introduced
        """
        self.hist_gui.insert(self.index, record)
        self.index += 1

        # add label to category list
        category = record.split(' | ')[2]
        self.history_categories[category] = self.history_categories.get(category, []) + [record]

    def delete_record(self, ind):
        """
        Delete record from listbox
        :param ind: index of record to be deleted
        """
        self.hist_gui.delete(ind)
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

    def load_records(self):
        """
        Fetch history records from a given file
        """

        def is_valid(line):
            """
            Check if record line is valid (date, timer and label)
            :param line: record to be checked
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

        # start load by asking for filename
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("Text files", '*.txt'),
                                                         ("All files", "*.*")))

        # cancel pressed
        if not filename:
            return

        try:
            with open(filename, 'r') as f:
                invalid_file = True
                for record in f:
                    record = record[:-1]
                    # if record respects format defined at the start of this function
                    if is_valid(record) and not self.is_duplicate(record):
                        invalid_file = False
                        self.add_record(record)

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
        if self.hist_gui.size() == 0:
            messagebox.showerror(title="Error", message="Cannot save empty list.")
            return

        filename = filedialog.asksaveasfilename(title="Save file",
                                                filetypes=(('Text files', '*.txt'),
                                                           ('All files', '*.*')),
                                                defaultextension=".txt")

        # cancel pressed
        if not filename:
            return

        try:
            with open(filename, 'w') as f:
                # iterate through records in list box, writing them to file
                for rec in range(self.hist_gui.size()):
                    f.write(self.hist_gui.get(rec))
        except FileNotFoundError:
            messagebox.showerror(title="Error", message="File not found.")
            # call function again
            self.save_records()

    def is_duplicate(self, record):
        """
        Given a certain record, iterates through existing list to see if it's a duplicate
        :param record: the record to be checked for duplicates
        :return: True if record is a duplicate, False otherwise
        """
        for ind in range(self.hist_gui.size()):
            rec = self.hist_gui.get(ind)
            print(rec, record)
            if rec == record:
                return True

        return False


class MainApp:
    def __init__(self, main_root):
        """
        Initializes main stopwatch app
        :param main_root: the root in which to display the app
        """
        # two tabs - stopwatch and history
        self.tab_control = ttk.Notebook(main_root)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab1, text='Stopwatch')
        self.tab_control.add(self.tab2, text='History')
        self.tab_control.pack()

        self.history = StopWatchHistory(self.tab2)
        self.stopwatch = StopWatch(self.tab1, self.history)


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('486x220')
    root.title('Stopwatch')
    root.resizable(False, False)

    app = MainApp(root)
    root.mainloop()
