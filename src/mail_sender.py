#!/usr/bin/python3

import re
import smtplib
from email import encoders
from email.header import Header
import mail_sender_conf as conf
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(to: str, subject: str, body: str, filename: str) -> bool:
    ''' Sends the given mail, returns True on success or False on failure. '''

    # Validate the receiver mail address with a regular expression.
    exp = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    if not re.fullmatch(exp, to):
        return False

    msg = MIMEMultipart()
 
    # Add all email headers
    msg["To"] = Header(to)
    msg["From"] = Header(conf.USERNAME)
    msg["Subject"] = Header(subject)
    
    # Add the given body to the message object.
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # Open file to add as attachment.
    try:
        with open(filename, "rb") as file:
            
            # The mail attachment is a binary file.
            attachment = MIMEBase("application", "octet-stream")
            attachment.set_payload(file.read())
    except:
        # File not found.
        return False

    # Remove path from header file name.
    filename = filename.split("/")[-1]

    # Encode and add header to the attachment.
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", f"attachment; filename= {filename}")

    # Combine attachment with body.
    msg.attach(attachment)

    # Connect to the mailserver.
    try:
        with smtplib.SMTP_SSL(conf.HOST, conf.PORT) as server:

            try:
                # Attempt to login to the mail server.
                server.login(conf.USERNAME, conf.PASSWORD)
            except:
                # Login failed.
                return False

            # Attempt to send the message, returns an error dictionary.
            err = server.sendmail(conf.USERNAME, to, msg.as_string())

            # Check if sending succeeded.
            if len(err) > 0:
                return False
    except:
        # Mailserver error.
        return False

    # Success.
    return True

if __name__ == "__main__":
    ''' Run simple demo. '''

    to = "<example@mymail.com>"
    subject = "Email Sender Test"
    body = "Sending my own code!"
    file = "mail_sender.py"

    print(f"Mail demo sent: {send_mail(to, subject, body, file)}")