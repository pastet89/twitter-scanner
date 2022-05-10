import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import EMAIL_SMTP_SERVER, EMAIL_USER, EMAIL_PASSWORD, FROM_EMAIL, TO_EMAIL


def email_notification(title, msg, email=TO_EMAIL):
    subject = "Twitter notification | " + title
    emsg = MIMEMultipart('alternative')
    body = MIMEText(msg, 'html')
    emsg.attach(body)
    from_ = f'Twitter Bot <{FROM_EMAIL}>'
    emsg['Subject'] = subject
    emsg['From'] = from_
    emsg['To'] = email

    password = EMAIL_PASSWORD
    username = EMAIL_USER
    server = smtplib.SMTP_SSL(EMAIL_SMTP_SERVER)
    server.login(username, password)
    server.sendmail(from_, email, emsg.as_string())
    server.close()
