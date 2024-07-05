import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from database.database import register_user, login_user
from datetime import datetime

class LoginDialog(tk.Frame):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.password_entry = None
        self.username_entry = None
        self.background_image_original = None
        self.background_image = None
        self.background_label = None
        self.on_success = on_success
        self.initUI()
        self.bind("<Configure>", self.on_resize)

    def initUI(self):
        self.configure(bg="white")
        self.clear_frame()
        self.load_background_image()

        tk.Label(self, text="Welcome to OmegaVR", font=("Helvetica", 24), bg="white").place(relx=0.5, y=50, anchor="n")
        tk.Label(self, text="Login", font=("Helvetica", 20), bg="white").place(relx=0.5, y=100, anchor="n")
        tk.Label(self, text="Username:", bg="white").place(relx=0.5, y=150, anchor="n")
        self.username_entry = tk.Entry(self)
        self.username_entry.place(relx=0.5, y=180, anchor="n")
        tk.Label(self, text="Password:", bg="white").place(relx=0.5, y=230, anchor="n")
        self.password_entry = tk.Entry(self, show='*')
        self.password_entry.place(relx=0.5, y=260, anchor="n")
        tk.Button(self, text="Login", command=self.login).place(relx=0.5, y=310, anchor="n")
        tk.Button(self, text="Register", command=self.setup_register).place(relx=0.5, y=350, anchor="n")

    def load_background_image(self):
        try:
            self.background_image_original = Image.open(os.path.join("assets", "background.png"))
            self.update_background_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load background image: {e}")

    def update_background_image(self):
        width = self.winfo_width()
        height = self.winfo_height()
        if width > 1 and height > 1:
            self.background_image = self.background_image_original.resize((width, height), Image.Resampling.LANCZOS)
            self.background_image = ImageTk.PhotoImage(self.background_image)
            if self.background_label is not None:
                self.background_label.config(image=self.background_image)
                self.background_label.image = self.background_image
            else:
                self.background_label = tk.Label(self, image=self.background_image)
                self.background_label.place(relwidth=1, relheight=1, x=0, y=0)
                self.background_label.lower()

    def on_resize(self, event):
        self.update_background_image()

    def setup_register(self):
        self.clear_frame()
        self.configure(bg="white")

        tk.Label(self, text="Register", font=("Helvetica", 20), bg="white").pack(pady=20)

        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=20)

        self.fields = {
            "Username": tk.Entry(form_frame),
            "Password": tk.Entry(form_frame, show="*"),
            "Accessibility Challenge": tk.Entry(form_frame),
            "Height (cm)": tk.Entry(form_frame),
            "Weight (kg)": tk.Entry(form_frame),
            "Eye Color": tk.Entry(form_frame),
            "IPD (mm)": tk.Entry(form_frame),
            "Astigmatism (Yes/No)": tk.Entry(form_frame),
            "Disabilities": tk.Entry(form_frame),
            "Gender": tk.Entry(form_frame),
            "Birthdate (YYYY-MM-DD)": tk.Entry(form_frame)
        }

        for idx, (field, entry) in enumerate(self.fields.items()):
            tk.Label(form_frame, text=field, bg="white").grid(row=idx, column=0, padx=10, pady=5, sticky="e")
            entry.grid(row=idx, column=1, padx=10, pady=5)

        tk.Button(self, text="Register", command=self.register).pack(pady=10)
        tk.Button(self, text="Back to Login", command=self.initUI).pack(pady=10)

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.background_label = None

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if login_user(username, password):
            self.on_success()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def register(self):
        data = {field: entry.get() for field, entry in self.fields.items()}

        # Basic validation
        if not data["Username"] or not data["Password"]:
            messagebox.showerror("Error", "Username and Password are required.")
            return

        # Validate Birthdate
        try:
            datetime.strptime(data["Birthdate (YYYY-MM-DD)"], "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid Birthdate format. Use YYYY-MM-DD.")
            return

        # Validate Height and Weight
        try:
            data["Height (cm)"] = float(data["Height (cm)"])
            data["Weight (kg)"] = float(data["Weight (kg)"])
            data["IPD (mm)"] = float(data["IPD (mm)"])
        except ValueError:
            messagebox.showerror("Error", "Height, Weight, and IPD must be numeric.")
            return

        # Validate Astigmatism
        if data["Astigmatism (Yes/No)"].lower() not in ["yes", "no"]:
            messagebox.showerror("Error", "Astigmatism must be 'Yes' or 'No'.")
            return

        # Register user
        if register_user(data):
            messagebox.showinfo("Success", "User registered successfully!")
            self.initUI()
        else:
            messagebox.showerror("Error", "Username already exists!")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = LoginDialog(root, on_success=lambda: print("Login successful!"))
    app.pack(fill="both", expand=True)
    root.mainloop()
