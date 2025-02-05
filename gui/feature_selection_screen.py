import tkinter as tk
from tkinter import messagebox
from gui.bulk_mail_screen import BulkMailScreen

class FeatureSelectionScreen:
    def __init__(self, root, logged_in_email, app_password):
        self.root = root
        self.logged_in_email = logged_in_email
        self.app_password = app_password

        self.feature_frame = tk.Frame(self.root)
        self.feature_frame.pack(fill="both", expand=True)

        tk.Label(self.feature_frame, text="Welcome!", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.feature_frame, text=f"Logged in as: {self.logged_in_email}", fg="blue").pack()

        tk.Button(self.feature_frame, text="Customised Bulk Mail (Excel)", command=self.show_bulk_mail_screen, width=30, bg="blue", fg="white").pack(pady=10)
        tk.Button(self.feature_frame, text="Bulk WhatsApp", command=lambda: messagebox.showinfo("Coming Soon", "This feature will be available in future updates!"), width=30).pack(pady=5)
        tk.Button(self.feature_frame, text="GUI Mail", command=lambda: messagebox.showinfo("Coming Soon", "This feature will be available in future updates!"), width=30).pack(pady=5)

    def show_bulk_mail_screen(self):
        self.feature_frame.destroy()
        BulkMailScreen(self.root, self.logged_in_email, self.app_password)
