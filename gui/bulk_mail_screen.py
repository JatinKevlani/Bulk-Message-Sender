import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from tkinter import ttk
import pandas as pd
import queue
import os
import re
import dns.resolver
from services.email_service import EmailService
from services.database_service import DatabaseService
from utils.threading_utils import start_thread

def check_email(email):
    """Validates email syntax and MX record"""
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return False

    domain = email.split("@")[1]
    
    try:
        records = dns.resolver.resolve(domain, "MX")
        return True if records else False
    except dns.resolver.NoAnswer:
        return False
    except dns.resolver.NXDOMAIN:
        return False
    except Exception as e:
        return False
   
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

        format_frame = tk.Frame(self.mail_frame)
        format_frame.pack(pady=5)
        bold_button = tk.Button(format_frame, text="Bold", command=self.make_bold)
        bold_button.pack(side=tk.LEFT, padx=2)
        italic_button = tk.Button(format_frame, text="Italic", command=self.make_italic)
        italic_button.pack(side=tk.LEFT, padx=2)
        underline_button = tk.Button(format_frame, text="Underline", command=self.make_underline)
        underline_button.pack(side=tk.LEFT, padx=2)

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
                email = row["Email"].strip()
                if not check_email(email):
                    self.log_queue.put(f"❌ Invalid Email: {email}\n")
                    continue

                personalized_body = body_template
                for column in columns:
                    placeholder = f"{{{column}}}"
                    personalized_body = personalized_body.replace(placeholder, str(row[column]))

                html_body = f"""
                <html>
                <body>
                    <p>{personalized_body.replace("\n", "<br>")}</p>
                </body>
                </html>
                """

                message = EmailService.create_email(
                    self.logged_in_email, row["Email"], subject, html_body, attachment_paths, is_html=True
                )
                messages.append((row["Email"], message))

                DatabaseService.log_email_to_firebase(
                    self.logged_in_email, row["Email"], subject, html_body, 
                    [os.path.basename(path) for path in attachment_paths]
                )

            self.progress_bar["maximum"] = len(messages)

            EmailService.send_emails(
                self.logged_in_email, self.app_password, messages, 
                self.progress_bar, self.log_queue
            ) 

            messagebox.showinfo("Success", "All emails sent successfully!")
            self.log_queue.put("🎉 SYSTEM: All emails sent successfully!\n")

        except Exception as e:
            self.log_queue.put(f"❌ Error: {str(e)}\n")

    def start_email_thread(self):
        start_thread(self.send_emails_thread)

    def make_bold(self):
        """Wraps the selected text with <b> and </b> tags."""
        try:
            start_index = self.body_text.index(tk.SEL_FIRST)
            end_index = self.body_text.index(tk.SEL_LAST)
            selected_text = self.body_text.get(start_index, end_index)
            self.body_text.delete(start_index, end_index)
            self.body_text.insert(start_index, f"<b>{selected_text}</b>")
        except tk.TclError:
            messagebox.showerror("Error", "Please select text to make bold.")

    def make_italic(self):
        """Wraps the selected text with <i> and </i> tags."""
        try:
            start_index = self.body_text.index(tk.SEL_FIRST)
            end_index = self.body_text.index(tk.SEL_LAST)
            selected_text = self.body_text.get(start_index, end_index)
            self.body_text.delete(start_index, end_index)
            self.body_text.insert(start_index, f"<i>{selected_text}</i>")
        except tk.TclError:
            messagebox.showerror("Error", "Please select text to make italic.")

    def make_underline(self):
        """Wraps the selected text with <u> and </u> tags."""
        try:
            start_index = self.body_text.index(tk.SEL_FIRST)
            end_index = self.body_text.index(tk.SEL_LAST)
            selected_text = self.body_text.get(start_index, end_index)
            self.body_text.delete(start_index, end_index)
            self.body_text.insert(start_index, f"<u>{selected_text}</u>")
        except tk.TclError:
            messagebox.showerror("Error", "Please select text to underline.")
