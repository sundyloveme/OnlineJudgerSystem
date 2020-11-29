import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

from_addr = "sunlittlewhile@163.com"
password = "l0ve2875106"
# to_addr = "656233622@qq.com"
smtp_server = "smtp.163.com"


# content = "" # 您的验证码是， 请勿泄露


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_email(to_addr, subject, content):
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
