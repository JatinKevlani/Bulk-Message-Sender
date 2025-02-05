import tkinter as tk
from gui.login_screen import LoginScreen

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulk Message Sender - Jatin Kevlani")
        self.root.geometry("500x600")
        self.show_splash_screen()

    def show_splash_screen(self):
        self.splash_frame = tk.Frame(self.root)
        self.splash_frame.pack(fill="both", expand=True)

        tk.Label(self.splash_frame, text="Bulk Message Sender", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self.splash_frame, text="by Jatin Kevlani", font=("Arial", 14)).pack()

        tk.Button(self.splash_frame, text="Login", command=self.show_login_screen, bg="blue", fg="white", font=("Arial", 12)).pack(pady=20)
        tk.Label(self.splash_frame, text="*By continuing you agree to terms and conditions*", font=("Arial", 8)).pack(pady=5)

    def show_login_screen(self):
        self.splash_frame.destroy()
        LoginScreen(self.root)
