import smtplib
import os
from email.message import EmailMessage

from dotenv import load_dotenv
# load environment variables from .env file
load_dotenv()

# function declaration - ensures autogen agents are aware of the function and particularly how to use it
send_email_declaration = {
    "name": "send_mail",
    "description": "Sends an email using SMTP with a specified subject, body, and recipient.",
    "parameters": {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "The subject of the email"
            },
            "body": {
                "type": "string",
                "description": "The body content of the email"
            },
            "to_email": {
                "type": "string",
                "description": "The recipient's email address"
            }
        },
        "required": ["subject", "body", "to_email"]
    },
}


def send_mail(subject, body, to_email):
    sender = "Automated Kirby <hiddenkirby@gmail.com>"

    message = EmailMessage()
    message.set_content(body)
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = to_email

    smtp_password = os.environ.get('SMTP_PASSWORD')  

    # using mailtrap for testing
    # needed to set up ahead of time
    with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
        server.login("f7d4c3d5fe2ee9", smtp_password)
        server.send_message(message)
        return "Email has been sent"


#  test function - ensure the above works as intended
# example usage:
# send_mail('subject', 'lorem ipsum', 'foo@bar.com')