import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from getDeng import getDeng
import traceback


def send_start_email(config, streamInfo):
    # send start notification
    msg = MIMEMultipart()
    msg["From"] = config["FROM_ADDRESS"]
    msg["To"] = ",".join(config["NOTIFY_USER"].values())
    msg["Subject"] = "{}开始直播{}".format(config['ROOM_NAME'], streamInfo['title'])
    body = "{}开始直播{}".format(config['ROOM_NAME'], streamInfo['title'])
    msg.attach(MIMEText(body, "plain"))
    email_session = smtplib.SMTP("smtp.gmail.com", 587)
    email_session.starttls()
    email_session.login(config["FROM_ADDRESS"], config["PASSWORD"])
    text = msg.as_string()
    email_session.sendmail(config["FROM_ADDRESS"], config["NOTIFY_USER"].values(), text)
    email_session.quit()


def send_ludeng(config, streamInfo):
    try:
        # send current ludeng with attached danmu record
        msg = MIMEMultipart()
        msg["From"] = config["FROM_ADDRESS"]
        msg["To"] = ",".join(config["LUDENG_USER"].values())
        msg["Subject"] = "{}于{}".format(config['ROOM_NAME'], streamInfo["danmu_file_name"][:-4].split("/", 2)[-1])
        body = getDeng(config, streamInfo)
        msg.attach(MIMEText(body, "plain"))
        p = MIMEBase("application", "octet-stream")
        with open(streamInfo["danmu_file_name"], "rb") as attachment:
            p.set_payload(attachment.read())
        encoders.encode_base64(p)
        p.add_header("Content-Disposition", "attachment", filename=streamInfo["danmu_file_name"].split("/", 2)[-1])
        msg.attach(p)  # 邮件附件是 filename
        email_session = smtplib.SMTP("smtp.gmail.com", 587)
        email_session.starttls()
        email_session.login(config["FROM_ADDRESS"], config["PASSWORD"])
        text = msg.as_string()
        email_session.sendmail(config["FROM_ADDRESS"], config["LUDENG_USER"].values(), text)
        email_session.quit()
    except Exception:
        with open("exception.txt", "a", encoding="utf-8") as log:
            log.write(traceback.format_exc())