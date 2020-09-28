"""Send email or text messages via python script.
You can only send 100 sms text messages per month!
Email has no restrictions
smpt gateway for orange mobile provider: https://business.orange.be/en/it-solutions/enterprise-messaging
script based on: https://dev.to/mraza007/sending-sms-using-python-jkd"""

import smtplib
from os.path import basename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import getpass
import datetime as dt

__author__ = "Willem Boone"
__email__ = "willem.boone@outlook.com"

# these variables are depending on you provider
MY_EMAIL = "willem.boone@outlook.com"
SMS_GATEWAY = "@sms.easymessaging.orange.be"
SMTP = "SMTP.office365.com"
PORT = 587


class SendMessage(object):
    def __init__(self, sms_gateway=SMS_GATEWAY, port=PORT, smtp=SMTP, my_email=MY_EMAIL):
        """can be used to sent sms text message or email
        Notice: only 100 sms text messages can be sent per month with orange
        Parameters:
        -----------
        provider(String): mobile provider, default is @sms.easymessaging.orange.be
        smtp(String): e-mail provider smtp, default is SMTP.office365.com
        port(int): port number matching smtp server, default is 587"""

        self.sms_gateway = sms_gateway
        self.smtp = smtp
        self.port = port
        self.my_email = my_email
        self.pas = getpass.getpass()

    def send_email(self, text, subject, receiver, files=None):

        server = smtplib.SMTP(self.smtp, self.port)
        server.starttls()
        server.login(self.my_email, self.pas)

        # structure our message
        msg = MIMEMultipart()
        msg['From'] = self.my_email
        msg['To'] = receiver

        # Make sure you add a new line in the subject
        msg['Subject'] = subject + "\n"
        # Make sure you also add new lines to your body
        body = text + "\n"

        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            msg.attach(part)

        # and then attach that body furthermore you can also send html content.
        msg.attach(MIMEText(body, 'plain'))
        message = msg.as_string()
        server.sendmail(self.my_email, receiver, message)

        # lastly quit the server
        server.quit()
        print("email has been sent to ", receiver, " @ ", dt.datetime.now())

    def send_sms(self, text, receiver):
        """sent message
        Parameters:
        -----------
        text(string): text message to sent, use \n for next line
        receiver(String or int): e-mail address or phone number, default is 32476013631"""

        sms_gateway = str(receiver) + self.sms_gateway
        print(sms_gateway)

        # Setup server
        server = smtplib.SMTP(self.smtp, self.port)
        server.starttls()
        server.login(self.my_email, self.pas)

        # structure our message
        msg = MIMEMultipart()
        msg['From'] = self.my_email
        msg['To'] = sms_gateway

        # Make sure you add a new line in the subject
        body = text + "\n"

        # and then attach that body furthermore you can also send html content.
        msg.attach(MIMEText(body, 'plain'))
        message = msg.as_string()
        server.sendmail(self.my_email, sms_gateway, message)

        # lastly quit the server
        server.quit()
        print("sms text has been sent to ", receiver, " @ ", dt.datetime.now())






