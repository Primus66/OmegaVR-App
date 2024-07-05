import tkinter as tk
from database.database import setup_db
from gui.login_dialog import LoginDialog
from gui.main_window import MainWindow


class EEGCalibrationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EEG Data Capture and Calibration")
        self.geometry("1200x800")
        self.setup_login()

    def setup_login(self):
        self.clear_frame()
        login_dialog = LoginDialog(self, self.setup_main_window)
        login_dialog.pack(fill=tk.BOTH, expand=1)

    def setup_main_window(self):
        self.clear_frame()
        main_window = MainWindow(self, self.exit_application)
        main_window.pack(fill=tk.BOTH, expand=1)

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def exit_application(self):
        self.quit()


if __name__ == "__main__":
    setup_db()
    app = EEGCalibrationApp()
    app.mainloop()
