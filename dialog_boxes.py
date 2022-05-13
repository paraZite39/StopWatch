import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


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
        if sure:
            self.canceled = True
            self.top.destroy()
