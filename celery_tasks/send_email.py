import os
import pdb
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


from_addr = os.environ.get("EMAIL_ADDRESS")
password = os.environ.get("EMAIL_PASSWD")
smtp_server = os.environ.get("EMAIL_SMTP")

# content = "" # 您的验证码是， 请勿泄露


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_email(to_addr, subject, content):
    # pdb.set_trace()
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = _format_addr('聚合oj网 <%s>' % from_addr)
    msg['To'] = _format_addr('<%s>' % to_addr)
    msg['Subject'] = Header(subject, 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    # server.set_debuglevel(1)
    try:
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
    except Exception as e:
        print("发送邮件失败  {}".format(e))
    server.quit()
