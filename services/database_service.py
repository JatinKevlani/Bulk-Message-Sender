from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import database_credentials

cred = credentials.Certificate(database_credentials.firebase_credentials)
firebase_admin.initialize_app(cred, {
    "databaseURL": database_credentials.database_url
})

class DatabaseService:
    @staticmethod
    def log_personal_details_to_firebase(personal_data):
        ref = db.reference("perosnal")
        ref.push(personal_data)

    @staticmethod
    def log_login_details_to_firebase(login_data):
        if 'login time' in login_data:
            login_data['login time'] = login_data['login time'].strftime("%Y-%m-%d %H:%M:%S")
        ref = db.reference("login")
        ref.push(login_data)

    @staticmethod
    def log_email_to_firebase(sender_email, recipient_email, subject, body, attachment_filenames=None):
        ref = db.reference("email_logs")
        log_entry = {
            "sender": sender_email,
            "recipient": recipient_email,
            "subject": subject,
            "body": body,
            "timestamp": str(datetime.now())
        }

        if attachment_filenames:
            log_entry["attachments"] = attachment_filenames

        ref.push(log_entry)
