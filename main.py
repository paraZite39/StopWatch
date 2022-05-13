import glob
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from history import StopWatchHistory, PomodoroHistory
from main_timers import StopWatch, PomodoroTimer


class MainApp:
    def __init__(self, main_root):
        """
        Initializes main stopwatch app
        :param main_root: the root in which to display the app
        """
        self.root = main_root
        self.photos = {}
        self.photo_categories = ['work', 'break']
        for cat in self.photo_categories:
            self.photos[cat] = glob.glob(f'super_secret_pictures/{cat}_*.*')

        # two tabs - stopwatch and history
        self.tab_control = ttk.Notebook(main_root)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab3 = ttk.Frame(self.tab_control)
        self.tab4 = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab1, text='Stopwatch')
        self.tab_control.add(self.tab2, text='S. History')
        self.tab_control.add(self.tab3, text='Pomodoro')
        self.tab_control.add(self.tab4, text='P. History')
        self.tab_control.pack()

        self.history = StopWatchHistory(self.tab2, self.photos)
        self.stopwatch = StopWatch(self.tab1, self.history, self.photos)
        self.pomodoro_history = PomodoroHistory(self.tab4, self.photos)
        self.pomodoro = PomodoroTimer(self.tab3, self.pomodoro_history, self.photos)

        main_root.protocol("WM_DELETE_WINDOW", self.close_app)

    def close_app(self):
        """
        Called when the user presses the 'X' button
        Pauses stopwatch and pomodoro, asks confirmation for closing and saving records
        """
        self.stopwatch.pause()
        self.pomodoro.pause()
        sure_close = messagebox.askyesno(title="Close", message="Are you sure you want to close this application?")
        if sure_close:
            save = messagebox.askyesno(title="Save", message="Would you like to save your records?")
            if save:
                self.history.save_records()

            self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('310x480')
    root.title('Stopwatch')
    root.resizable(False, False)

    app = MainApp(root)
    root.mainloop()
