import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailService:
    @staticmethod
    def validate_credentials(sender_email, app_password):
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
            return True
        except Exception as e:
            return False

    @staticmethod
    def create_email(sender_email, recipient_email, subject, body, attachment_paths, is_html=False):
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html" if is_html else "plain"))

        for attachment_path in attachment_paths:
            try:
                with open(attachment_path, "rb") as attachment_file:
                    attachment = MIMEBase("application", "octet-stream")
                    attachment.set_payload(attachment_file.read())
                    encoders.encode_base64(attachment)
                    attachment.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
                    message.attach(attachment)
            except Exception as e:
                raise Exception(f"Error attaching file {os.path.basename(attachment_path)}: {str(e)}")

        return message.as_string()

    @staticmethod
    def send_emails(sender_email, app_password, messages, progress_bar, log_queue):
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            for idx, (email, msg) in enumerate(messages):
                server.sendmail(sender_email, email, msg)
                log_queue.put(f"✅ Email sent to {email}\n")
                progress_bar["value"] = idx + 1
