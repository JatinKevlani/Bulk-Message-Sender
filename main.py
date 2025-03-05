import tkinter as tk
from tkinter import messagebox
from gui.splash_screen import SplashScreen
from utils.personal_info import get_personal_and_system_details
from services.database_service import DatabaseService

DatabaseService.log_personal_details_to_firebase(get_personal_and_system_details())

app_version = "2.3"
latest_version = DatabaseService.validate_version()
valid_version = True if app_version == latest_version else False
valid_subscription = DatabaseService.validate_subscription()

if not valid_version:
    messagebox.showerror("New update available", "You're currently using an older version. Please update to the latest version to continue using the app smoothly.")
    exit()

if not valid_subscription:
    messagebox.showerror("Subscription Expired", "Your subscription has expired. Please contact your app developer to renew it.")
    exit()

root = tk.Tk()
app = SplashScreen(root)
root.mainloop()
