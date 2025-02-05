import tkinter as tk
from tkinter import filedialog, scrolledtext
from tkinter import ttk
import pandas as pd
import queue
import os
from services.email_service import EmailService
from services.database_service import DatabaseService
from utils.threading_utils import start_thread

class BulkMailScreen:
    def __init__(self, root, logged_in_email, app_password):
        self.root = root
        self.logged_in_email = logged_in_email
        self.app_password = app_password
        self.log_queue = queue.Queue()

        self.mail_frame = tk.Frame(self.root)
        self.mail_frame.pack(fill="both", expand=True)

        tk.Label(self.mail_frame, text="Customised Bulk Mail (Excel)", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.mail_frame, text="Subject:").pack()
        self.subject_entry = tk.Entry(self.mail_frame, width=50)
        self.subject_entry.pack()

        tk.Label(self.mail_frame, text="Email Body:").pack()
        self.body_text = scrolledtext.ScrolledText(self.mail_frame, width=50, height=5)
        self.body_text.pack()

        self.file_label = tk.Label(self.mail_frame, text="No file selected", fg="red")
        self.file_label.pack()
        tk.Button(self.mail_frame, text="Select Email Excel File", command=self.select_file).pack()

        self.attach_file_label = tk.Label(self.mail_frame, text="No attachment selected", fg="red")
        self.attach_file_label.pack()
        tk.Button(self.mail_frame, text="Select Attachment", command=self.select_attachment).pack()

        tk.Button(self.mail_frame, text="Send Emails", command=self.start_email_thread, bg="green", fg="white").pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.mail_frame, length=400, mode="determinate")
        self.progress_bar.pack(pady=10)

        tk.Label(self.mail_frame, text="Log:").pack()
        self.log_area = scrolledtext.ScrolledText(self.mail_frame, width=60, height=10)
        self.log_area.pack()
        self.log_area.insert(tk.END, f"🟢 Logged in as: {self.logged_in_email}\n\n")

        self.root.after(100, self.update_log)

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        self.file_label.config(text="Selected: " + self.file_path)

    def select_attachment(self):
        self.attachment_paths = filedialog.askopenfilenames(filetypes=[("All Files", "*.*")])
        if self.attachment_paths:
            self.attach_file_label.config(text="Selected: " + ", ".join([os.path.basename(path) for path in self.attachment_paths]))
        else:
            self.attach_file_label.config(text="No attachment selected", fg="red")

    def update_log(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self.log_area.insert(tk.END, msg)
            self.log_area.see(tk.END)
        self.root.after(100, self.update_log)

    def send_emails_thread(self):
        try:
            df = pd.read_excel(self.file_path, engine="openpyxl")
            columns = df.columns.tolist()

            subject = self.subject_entry.get()
            body_template = self.body_text.get("1.0", tk.END).strip()

            if not subject or not body_template:
                self.log_queue.put("❌ Error: Please fill in all fields!\n")
                return

            attachment_paths = getattr(self, 'attachment_paths', [])

            messages = []
            for _, row in df.iterrows():
                personalized_body = body_template
                for column in columns:
                    placeholder = f"{{{column}}}"
                    personalized_body = personalized_body.replace(placeholder, str(row[column]))

                message = EmailService.create_email(self.logged_in_email, row["Email"], subject, personalized_body, attachment_paths)
                messages.append((row["Email"], message))

                DatabaseService.log_email_to_firebase(self.logged_in_email, row["Email"], subject, personalized_body, [os.path.basename(path) for path in attachment_paths])

            self.progress_bar["maximum"] = len(messages)

            EmailService.send_emails(self.logged_in_email, self.app_password, messages, self.progress_bar, self.log_queue)

            self.log_queue.put("🎉 SYSTEM: All emails sent successfully!\n")

        except Exception as e:
            self.log_queue.put(f"❌ Error: {str(e)}\n")

    def start_email_thread(self):
        start_thread(self.send_emails_thread)
