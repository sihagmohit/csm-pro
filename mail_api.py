# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import constants
sample_html = """\
<html>
<head>
</head><body>
<h1> hello THERE</h1>
</body>
</html>
"""
def send_mail(clients=["siddharth@cyronics.com"],subject='Test API',html_content='<strong>and easy to do anywhere, even with Python</strong>' ):
    # mail options
    #admin@cyronics.com
    #alerts.cyronics@gmail.com
    if constants.SEND_MAIL:
        message = Mail(
            from_email='alerts.cyronics@gmail.com',
            to_emails=clients,
            subject=subject,
            html_content=html_content)
        try:
            sg = SendGridAPIClient("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")
            response = sg.send(message)

            print("########################################MAILS WERE SENT#####################################################")
            # return response.status_code
        except Exception as e:
            #return e.message
            print("################################### Error occurred while sending mails! #####################################")

# VATSAL
def send_mail_via_smtp(clients=["vatsalrana14@gmail.com"], subject="Reports", html_content=""):
    smtp_server = "zimsmtp.logix.in"
    port = 587  # For starttls
    sender_email = "iotreports@ppapco.com"
    password = "Reports@98765"

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email


    # Backup text.
    text = """\
    Failed to generate report links. Please log on to http://oee.ppapco.in.
    """
    # HTML content
    html = html_content

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    for email in clients:
        print(email)
        message["To"] = email
        try:
            server = smtplib.SMTP(smtp_server, port)
            print("connected!")
            server.ehlo()
            server.starttls(context=context)  # Secure the connection
            server.ehlo()
            server.login(sender_email, password)
            res = server.sendmail(sender_email, email, message.as_string())
            print(res)
            print("MAIL WAS SENT VIA SMTP")

            server.quit()

        except Exception as e:
            # Print any error messages to stdout
            print("SMTP FAILED!")
            print(e)


# VATSAL
def send_mail_only_text_content(clients=["siddharth@cyronics.com"],subject='Test API',content='test content' ):
    # mail options
    #admin@cyronics.com
    #alerts.cyronics@gmail.com
    message = Mail(
        from_email='alerts.cyronics@gmail.com',
        to_emails=clients,
        subject=subject,
        plain_text_content=content)
    try:
        sg = SendGridAPIClient("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")
        response = sg.send(message)

        print("########################################MAILS WERE SENT#####################################################")
        # return response.status_code
    except Exception as e:
        #return e.message
        print("################################### Error occurred while sending mails! #####################################")

