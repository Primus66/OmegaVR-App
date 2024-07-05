import tkinter as tk


class ElectrodeStatusPage(tk.Frame):
    def __init__(self, parent, electrode_status):
        super().__init__(parent)
        self.electrode_status = electrode_status
        self.initUI()

    def initUI(self):
        self.configure(bg="white")
        tk.Label(self, text="Electrode Status", font=("Helvetica", 20), bg="white").pack(pady=10)

        for idx, status in enumerate(self.electrode_status):
            color = "green" if status else "red"
            tk.Label(self, text=f"Electrode {idx + 1}: {'Active' if status else 'Inactive'}",
                     font=("Helvetica", 15), bg=color, width=20).pack(pady=5)

    def update_status(self, new_status):
        self.electrode_status = new_status
        for widget in self.winfo_children():
            widget.destroy()
        self.initUI()
