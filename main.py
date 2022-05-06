from datetime import date
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import filedialog


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

        self.label = tk.Label(top, text="What did you do during this time? (10 chars max)")
        self.label.grid(row=0, padx=10, pady=10)

        self.myEntryBox = tk.Entry(top)
        self.myEntryBox.grid(row=0, column=1, padx=10, pady=10)

        self.cat_label = tk.Label(top, text="What category does this label go into?")
        self.cat_label.grid(row=1, column=0)

        self.cat_input = tk.StringVar()
        self.category_combo = ttk.Combobox(top, textvariable=self.cat_input, values=categories)
        self.category_combo.grid(row=1, column=1, padx=10)

        self.mySubmitButton = tk.Button(top, text='Submit', command=self.send)
        self.mySubmitButton.grid(row=2, column=0, padx=10, pady=10)

    def send(self):
        """
        Submit button pressed, set final label and category values and destroy pop-up
        :return:
        """
        self.final_label = self.myEntryBox.get()
        self.final_category = self.cat_input.get()
        self.top.destroy()


class StopWatch:
    def __init__(self, watch_root, hist):
        """
        Initializes stopwatch
        :param watch_root: tk root in which to put the elements
        :param hist: stopwatch history in which to store records
        """
        self.hist = hist
        self.root = watch_root

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

        category_values = self.hist.history_categories.keys()
        res = LabelDialog(self.root, tuple(category_values))
        self.root.wait_window(res.top)

        lab = res.final_label

        while 0 >= len(lab) or len(lab) > 10:
            res = LabelDialog(self.root, tuple(category_values))

        final_label = res.final_label
        final_category = res.final_category

        # adds record with today's date, current timer and provided category
        formatted_label = " | ".join([date.today().strftime("%d/%m/%Y"), self.get_label(), final_label])
        self.hist.add_record(formatted_label, final_category)
        self.start_button.configure(state=tk.ACTIVE)
        self.reset()


class StopWatchHistory:
    def __init__(self, hist_root):
        """
        Initializes stopwatch history
        :param hist_root: the root in which to show the history
        """
        self.hist_root = hist_root
        self.history_categories = {'Work': [], 'Study': [], 'Exercise': [], 'Other': []}
        self.index = 1
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

        self.button_frame = tk.Frame(self.f, pady=5)
        self.button_frame.pack(side=tk.BOTTOM)
        self.delete_button = tk.Button(self.button_frame, text='Delete')
        self.delete_button.pack(side=tk.LEFT)
        self.delete_button.configure(state=tk.DISABLED)

        self.load_button = tk.Button(self.button_frame, text='Load', command=self.load_records)
        self.load_button.pack(side=tk.LEFT)
        self.save_button = tk.Button(self.button_frame, text='Save', command=self.save_records)
        self.save_button.pack(side=tk.LEFT)

        self.hist_gui.bind("<ButtonRelease-1>", self.onselect)

    def init_tree(self):
        for ind, cat in enumerate(self.history_categories.keys()):
            self.hist_gui.insert(parent='', index='end', iid=cat, text=cat, values=())

    def onselect(self, _):
        """
        Update the right frame when a record from tree is selected
        :param _:
        :param e: selection event
        """
        date, length, label = None, None, None

        selection = self.hist_gui.focus()

        if not selection:
            return

        category = self.hist_gui.parent(selection)
        vals = self.hist_gui.item(selection, 'values')

        # no record is selected => return
        if not vals:
            return

        print(vals)

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
        self.history_categories[category] = self.history_categories.get(category, []) + [record]
        self.hist_gui.insert(parent=category, index=self.index, text="", values=(date, length, label))
        self.index += 1
        print(self.history_categories)

    def delete_record(self, ind, label, category):
        """
        Delete record from treeview
        :param label: record to be deleted
        """
        self.hist_gui.delete(ind)
        print(label, category, self.history_categories[category])
        self.history_categories[category].remove(label)
        self.reset_labels()

        if self.hist_gui.size() == 0:
            self.delete_button.configure(state=tk.DISABLED)

        print(self.history_categories)

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

        def is_valid(label):
            """
            Check if record line is valid (date, timer and label)
            :param label: record to be checked
            :return: True if record is valid, False otherwise
            """

            import re

            elements = label.split(' | ')
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
                    record = record.strip('\n')
                    if len(record.split('\t')) == 2:
                        label, category = record.split('\t')
                        print('label, category', label, category)
                        # if record respects format defined at the start of this function
                        print(is_valid(label), self.is_duplicate(label, category), category in self.history_categories.keys())
                        if is_valid(label) and not self.is_duplicate(label, category) \
                                and category in self.history_categories.keys():
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
