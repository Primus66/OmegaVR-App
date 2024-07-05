import csv
import os
import random
import tkinter as tk
from tkinter import messagebox, filedialog
import numpy as np
from PIL import Image, ImageTk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import boto3
from botocore.exceptions import NoCredentialsError


def generate_realistic_eeg_data():
    time = np.linspace(0, 1, 100)
    eeg_data = [np.sin(2 * np.pi * 10 * time) + np.random.randn(100) * 0.1 for _ in range(6)]
    return eeg_data


def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client(
        's3',
        aws_access_key_id='YOUR_ACCESS_KEY',
        aws_secret_access_key='YOUR_SECRET_KEY',
        region_name='us-east-1'  # Specify your region here
    )
    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


class MainWindow(tk.Frame):
    def __init__(self, parent, exit_callback):
        super().__init__(parent)
        self.parent = parent
        self.exit_callback = exit_callback
        self.calibration_data = []
        self.calibrating = False  # Track calibration state
        self.electrode_status = [True] * 6  # Fixed and active
        self.initUI()

    def initUI(self):
        self.configure(bg="white")

        # Frame for calibration graph and task image
        self.left_frame = tk.Frame(self, bg="white")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.right_frame = tk.Frame(self, bg="white")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

        # Calibration graph
        self.fig, self.axs = plt.subplots(6, 1, figsize=(5, 12), dpi=100)
        self.fig.tight_layout(pad=3.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.left_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Task image
        self.image_label = tk.Label(self.right_frame, bg="white")
        self.image_label.pack(pady=20)

        # Instructions and progress
        self.instruction_label = tk.Label(self.right_frame, text="", font=("Helvetica", 15), bg="white")
        self.instruction_label.pack(pady=20)
        self.progress_bar = tk.Label(self.right_frame, text="Progress: 0/4", font=("Helvetica", 12), bg="white")
        self.progress_bar.pack(pady=5)
        self.start_button = tk.Button(self.right_frame, text="Start Calibration", command=self.start_calibration)
        self.start_button.pack(pady=10)
        tk.Button(self.right_frame, text="Save Data", command=self.save_data).pack(pady=10)
        self.electrode_status_button = tk.Button(self.right_frame, text="Electrode Status",
                                                 command=self.show_electrode_status)
        self.electrode_status_button.pack(pady=10)

        # Small icon in the bottom left corner
        self.small_icon_label = tk.Label(self.left_frame, bg="white")
        self.small_icon_label.place(relx=0.0, rely=1.0, anchor='sw')

    def start_calibration(self):
        if not self.calibrating:  # Only start if not already calibrating
            self.calibrating = True
            self.start_button.config(text="Calibrating...", state=tk.DISABLED)
            self.electrode_status_button.config(state=tk.DISABLED)
            self.actions = ["Left Click", "Right Click", "Scroll Up", "Scroll Down"]
            self.calibration_data = {action: [] for action in self.actions}
            self.current_action = 0
            self.next_calibration_step()

    def next_calibration_step(self):
        if self.current_action < len(self.actions):
            action = self.actions[self.current_action]
            self.instruction_label.config(text=f"Prepare for {action}")
            self.show_calibration_image(action)
            self.after(3000, lambda: self.perform_action(action))
        else:
            self.complete_calibration()

    def perform_action(self, action):
        self.instruction_label.config(text=f"Now {action}")
        self.capture_eeg_data(action)
        self.after(5000, self.next_calibration_step)  # Perform action for 5 seconds

    def show_calibration_image(self, action):
        image_file_map = {
            "Left Click": "left_click.png",
            "Right Click": "right_click.png",
            "Scroll Up": "scroll_up.png",
            "Scroll Down": "scroll_down.png"
        }
        image_path = os.path.join("gui", "calibration_images", image_file_map[action])
        try:
            image = Image.open(image_path)
            image = image.resize((200, 200))
            image = ImageTk.PhotoImage(image)
            self.image_label.config(image=image)
            self.image_label.image = image
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image for {action}: {e}")

        # Display small icon
        small_icon_path = os.path.join("gui", "calibration_images", "small_icon.png")
        try:
            small_icon = Image.open(small_icon_path)
            small_icon = small_icon.resize((50, 50))
            small_icon = ImageTk.PhotoImage(small_icon)
            self.small_icon_label.config(image=small_icon)
            self.small_icon_label.image = small_icon
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load small icon: {e}")

    def capture_eeg_data(self, action):
        eeg_data = generate_realistic_eeg_data()
        self.calibration_data[action].append(eeg_data)
        for i, ax in enumerate(self.axs):
            ax.clear()
            ax.plot(eeg_data[i])
            ax.set_title(f"EEG Data - Electrode {i + 1} - {action}")
        self.fig.tight_layout(pad=3.0)
        self.canvas.draw()
        self.current_action += 1
        self.progress_bar.config(text=f"Progress: {self.current_action}/{len(self.actions)}")

    def complete_calibration(self):
        messagebox.showinfo("Calibration Complete", "Calibration is complete!")
        self.instruction_label.config(text="Calibration Complete")
        self.image_label.config(image='')
        self.image_label.image = None
        self.start_button.config(text="Start Calibration", state=tk.NORMAL)
        self.electrode_status_button.config(state=tk.NORMAL)
        self.calibrating = False  # Reset calibration state

    def save_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                for action, data in self.calibration_data.items():
                    writer.writerow([action])
                    for row in zip(*data):
                        writer.writerow(row)
            messagebox.showinfo("Success", "Data saved successfully!")

            # Upload to AWS
            bucket = 'your-bucket-name'
            s3_file = os.path.basename(file_path)
            if upload_to_aws(file_path, bucket, s3_file):
                messagebox.showinfo("Success", "Data uploaded to AWS S3 successfully")
            else:
                messagebox.showerror("Error", "Failed to upload data to AWS S3")

            if messagebox.askyesno("Exit Application", "Do you want to exit the application?"):
                self.exit_callback()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")

    def show_electrode_status(self):
        status_message = "\n".join([f"Electrode {i + 1}: {'Active' if status else 'Inactive'}"
                                    for i, status in enumerate(self.electrode_status)])
        messagebox.showinfo("Electrode Status", status_message)


def main():
    root = tk.Tk()
    root.title("OmegaVR EEG Calibration")
    root.geometry("1200x800")
    app = MainWindow(root, exit_callback=root.quit)
    app.pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()
