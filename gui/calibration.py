import numpy as np
import cv2
import tkinter as tk
from PIL import Image, ImageTk

class CalibrationTool(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Eye Tracking Calibration")
        self.geometry("800x600")
        self.canvas = tk.Canvas(self, width=800, height=600)
        self.canvas.pack()
        self.image_label = tk.Label(self)
        self.image_label.pack()
        self.cap = cv2.VideoCapture(0)  # Use the correct camera index for your setup
        self.distortion_parameters = None
        self.start_calibration()

    def start_calibration(self):
        self.after(100, self.update_frame)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = self.apply_barrel_distortion(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
            self.image_label.image = image
        self.after(100, self.update_frame)

    def apply_barrel_distortion(self, image):
        if self.distortion_parameters is None:
            self.distortion_parameters = self.calculate_distortion_parameters(image)
        k1, k2, k3, p1, p2 = self.distortion_parameters
        h, w = image.shape[:2]
        fx = fy = w / 2
        cx = cy = w / 2
        camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
        dist_coeffs = np.array([k1, k2, p1, p2, k3])
        return cv2.undistort(image, camera_matrix, dist_coeffs)

    def calculate_distortion_parameters(self, image):
        # Placeholder values for the distortion parameters
        k1 = -0.5
        k2 = 0.2
        k3 = 0.0
        p1 = 0.0
        p2 = 0.0
        return k1, k2, k3, p1, p2

    def close(self):
        self.cap.release()
        self.destroy()
