import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import filedialog
import re


class History:
    def __init__(self, hist_root, columns, labels, uses_categories, photos, init_file):
        self.root = hist_root

        self.photos = photos
        self.init_file = init_file
        self.uses_categories = uses_categories

        if self.uses_categories:
            self.history_categories = {col: [] for col in ['Work', 'Study', 'Exercise', 'Other']}
        else:
            self.history_categories = {}

        self.index = 0

        # treeview for history records
        self.hist_gui = ttk.Treeview(hist_root)
        self.tree_width = 300
        self.columns = columns
        self.hist_gui['columns'] = columns
        self.hist_gui.grid(row=0, column=0, columnspan=2)

        # respond to click on the treeview
        self.hist_gui.bind("<ButtonRelease-1>", self.onselect)

        # frame for buttons (delete, load, save)
        self.button_frame = tk.Frame(hist_root, pady=5)
        self.button_frame.grid(row=1, column=0, columnspan=3)
        self.delete_button = tk.Button(self.button_frame, text='Delete')
        self.delete_button.pack(side=tk.LEFT)
        self.delete_button.configure(state=tk.DISABLED)

        self.load_button = tk.Button(self.button_frame, text='Load', command=self.load_records)
        self.load_button.pack(side=tk.LEFT)
        self.save_button = tk.Button(self.button_frame, text='Save', command=self.save_records)
        self.save_button.pack(side=tk.LEFT)

        # detail frame
        self.f = tk.Frame(hist_root, height=350)
        self.f.grid(row=2, column=0, columnspan=2, padx=10, pady=20)
        self.labels = labels or columns
        self.label_widgets = self._init_labels()

        # fetch records from init file, initialize tree
        self._init_tree()
        self._initialize_cols_headings()
        self._init_fetch()

    def _init_labels(self):
        widgets = [tk.Label(self.f, text=f'{label}: ', font=('Arial', 12)) for label in self.labels]

        for wid in widgets:
            wid.pack(anchor="e")

        return widgets

    def reset_labels(self):
        for label, widget in zip(self.labels, self.label_widgets):
            widget.configure(text=f'{label}: ')

    def _init_fetch(self):
        try:
            self.load_records(self.init_file)
        except FileNotFoundError:
            pass

    def _initialize_cols_headings(self):
        col_width = self.tree_width // len(self.columns)
        first_col_title, first_col_width = "", 5

        if len(self.history_categories.keys()) > 0:
            col_width = self.tree_width // (len(self.columns) + 1)
            first_col_title, first_col_width = "Category", col_width

        self.hist_gui.column("#0", width=first_col_width)
        self.hist_gui.heading("#0", text=first_col_title, anchor=tk.W)

        for col in self.columns:
            self.hist_gui.column(col, width=col_width, anchor=tk.CENTER)
            self.hist_gui.heading(col, text=col, anchor=tk.CENTER)

    def load_records(self, filename=None, show_error=False):
        if not filename:
            # start load by asking for filename
            filename = filedialog.askopenfilename(title="Open file",
                                                  filetypes=(("Text files", '*.txt'),
                                                             ("All files", "*.*")),
                                                  initialfile=self.init_file)

        # cancel pressed
        if not filename:
            return

        try:
            with open(filename, 'r') as f:
                # invalid file = no usable records / all duplicates
                invalid_file = True
                for record in f:
                    record = record.strip('\n')
                    if self.uses_categories:
                        # label and category, split by tab '\t'
                        label, category = record.split('\t')
                    else:
                        label, category = record, None

                    # if record respects format, isn't duplicate and category is valid
                    if self.is_valid(label) and not self.is_duplicate(label, category) \
                            and (not self.uses_categories or category in self.history_categories.keys()):
                        # file isn't invalid, as a record was found
                        invalid_file = False
                        self.add_record(label, category)

                # no valid records found in file
                if show_error and invalid_file:
                    messagebox.showerror(title="Error", message="No useful records found on file.")

        except FileNotFoundError:
            messagebox.showerror(title="Error", message="File not found.")
            # call function again
            self.load_records()

    def save_records(self, use_categories=False):
        """
        Save records to a given filename
        """

        total_len = 0
        if self.uses_categories:
            for parent in self.hist_gui.get_children():
                total_len += len([ch for ch in self.hist_gui.get_children(parent)])
        else:
            total_len += len(self.hist_gui.get_children())

        print(total_len)

        if total_len == 0:
            messagebox.showerror(title="Error", message="Cannot save empty list.")
            return

        # prompt for filename
        filename = filedialog.asksaveasfilename(title="Save file",
                                                filetypes=(('Text files', '*.txt'),
                                                           ('All files', '*.*')),
                                                defaultextension=".txt",
                                                initialfile=self.init_file)

        # cancel pressed
        if not filename:
            return

        with open(filename, 'w') as f:
            if use_categories:
                # iterate through records in list box, writing them to file
                for category in self.history_categories:
                    records = self.history_categories[category]
                    for line in records:
                        write_line = line + "\t" + category + "\n"
                        f.write(write_line)
            else:
                for record in self.hist_gui.get_children():
                    item = self.hist_gui.item(record)['values']
                    write_line = " | ".join(item) + "\n"
                    f.write(write_line)

    def onselect(self, _):
        """
        Update the right frame when a record from tree is selected
        :param _: event parameter, not used
        """
        # take selected treeview item
        selection = self.hist_gui.focus()

        if not selection:
            return

        # take selected item's parent (category)
        category = self.hist_gui.parent(selection)
        # take selected item's values (date, length, label)
        vals = self.hist_gui.item(selection, 'values')

        # no record is selected => return
        if not vals or len(vals) != len(self.labels):
            return

        # update labels with record data
        for label, widget, val in zip(self.labels, self.label_widgets, vals):
            widget.configure(text=label + ": " + (val or 'null'))

        # activate delete button
        self.delete_button.configure(state=tk.ACTIVE,
                                     command=lambda: self.delete_record(selection, ' | '.join(vals), category))

    def add_record(self, record, category):
        cols = record.split(' | ')

        if len(cols) != len(self.columns):
            return

        if not self.is_duplicate(record, category):

            # add record to category dict
            if category:
                self.history_categories[category] = self.history_categories.get(category, []) + [record]

            # add record to treeview
            self.hist_gui.insert(parent=category or '', index=self.index, text="", values=tuple(cols))
            self.index += 1
        else:
            messagebox.showerror(title="Duplicate label", message="Duplicate label, please try again.")
            new_record, new_label = None, ''
            # if label is empty, duplicate or too long
            while (not new_record or not new_label
                   or self.is_duplicate(new_record, category) or len(new_label) > 10):
                new_label = simpledialog.askstring("New label", prompt="Please enter new label:")
                new_record = ' | '.join(cols[:-1].append(new_label or 'default'))

            self.add_record(new_record, category)

    def delete_record(self, ind, record, category):
        """
        Delete record from treeview
        :param category: record's category
        :param ind: record's index
        :param record: record to be deleted
        """
        # delete record from treeview (with index)
        self.hist_gui.delete(ind)

        if category:
            # delete record from category dict
            self.history_categories[category].remove(record)

        self.reset_labels()

        if self.hist_gui.size() == 0:
            self.delete_button.configure(state=tk.DISABLED)

    # FUNCTIONS TO BE IMPLEMENTED BY EACH HISTORY INSTANCE
    def _init_tree(self):
        raise NotImplementedError

    def is_valid(self, label):
        raise NotImplementedError

    def is_duplicate(self, label, category):
        raise NotImplementedError


class StopWatchHistory(History):
    def __init__(self, hist_root, photos, init_file='stopwatch_history.txt'):
        """
        Initializes stopwatch history
        When application is started, it will search for file 'history.txt'
        :param hist_root: the root in which to show the history
        """
        super().__init__(hist_root, ['Date', 'Length', 'Label'], ['Date', 'Length', 'Label'], True, photos, init_file)

    def _init_tree(self):
        """
        Takes categories from the 'history_categories' dict and inserts them in treeview
        """
        for ind, cat in enumerate(self.history_categories.keys()):
            print(ind, cat)
            self.hist_gui.insert(parent='', index=ind, iid=cat, text=cat, values=())

    def is_valid(self, line):
        """
        Check if record line is valid (date, timer and label)
        :param line: line to be checked
        :return: True if record is valid, False otherwise
        """
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


class PomodoroHistory(History):
    def __init__(self, hist_root, photos, init_file="pomodoro_history.txt"):
        super().__init__(hist_root, ["Date", "Label"], ["Date", "Label"], False, photos, init_file)

    def _init_tree(self):
        pass

    def is_valid(self, line):
        """
        Check if record line is valid (date and label)
        :param line: line to be checked
        :return: True if record is valid, False otherwise
        """
        elements = line.split(' | ')
        if len(elements) == 2:
            # record contains a date of format dd/mm/yyyy
            valid_date = re.match(r"^\d{2}/\d{2}/\d{4}$", elements[0])
            # record contains a label (break or focus)
            valid_label = re.match(r"^(break|work)$", elements[1])

            if valid_date and valid_label:
                return True

        return False

    def add_record(self, record, category=None):
        date, label = record.split(' | ')

        # add record to treeview
        self.hist_gui.insert(parent='', index=self.index, text="", values=(date, label))
        self.index += 1

    def delete_record(self, ind, label, _):
        # delete record from treeview (with index)
        self.hist_gui.delete(ind)

        self.reset_labels()

        if self.hist_gui.size() == 0:
            self.delete_button.configure(state=tk.DISABLED)

    def is_duplicate(self, label, category=None):
        return False
