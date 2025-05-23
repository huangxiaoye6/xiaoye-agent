from .celery import celery
from utils.send_email import send_email

@celery.task
def celery_send_email(email_account,subject,content):
    send_email(email_account,subject,content)
    msg='{0}邮箱：发送成功'.format(email_account)
    return msg




