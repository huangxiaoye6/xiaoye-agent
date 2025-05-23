import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from settings import EMAIL_FROM,EMAIL_HOST,EMAIL_PORT,EMAIL_HOST_USER,EMAIL_HOST_PASSWORD

def send_email(email_account,subject,content):
    msg=MIMEText(content,'plain','utf-8')
    msg['From'] = EMAIL_FROM  # 发件人邮箱
    msg['To']=email_account  # 收件人邮箱
    msg['Subject']=subject  # 邮箱主题
    server=smtplib.SMTP_SSL(EMAIL_HOST)
    server.connect(EMAIL_HOST, EMAIL_PORT)
    server.login(EMAIL_HOST_USER,EMAIL_HOST_PASSWORD)
    server.sendmail(EMAIL_FROM,email_account,msg=msg.as_string())
    server.quit()

def send_file_email(email_account,subject,content):
    attachment_path='{0}/{1}.log'.format(LOGS_DIR,datetime.now().strftime('%Y-%m-%d'))
    msg=MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To']=email_account
    msg['Subject']=subject
    msg.attach(MIMEText(content, 'plain'))
    with open(attachment_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {attachment_path.split("/")[-1]}')
        msg.attach(part)
    server=smtplib.SMTP_SSL(EMAIL_HOST)
    server.connect(EMAIL_HOST, EMAIL_PORT)
    server.login(EMAIL_HOST_USER,EMAIL_HOST_PASSWORD)
    server.sendmail(EMAIL_FROM,email_account,msg=msg.as_string())
    server.quit()