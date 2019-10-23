from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib
import time
import const

def _init_email_template():
    with open('templates/email.html', 'r',encoding='UTF-8') as f:
        const._EMAIL_TEMPLATE = f.read()

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def _send_reset_password_email(username,to_addr,url):
    from_addr = 'wujiezhaojun@126.com'
    password = '910421Zj!'
    smtp_server = 'smtp.126.com'
    
    html = const._EMAIL_TEMPLATE
    html = html.replace("{{username}}",username)

    #获取当前时间
    time_now = int(time.time())
    #转换成localtime
    time_local = time.localtime(time_now)
    #转换成新的时间格式(2016-05-09 18:59:20)
    dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)


    html = html.replace("{{time}}",dt)
    html = html.replace("{{reseturl}}",url)


    msg = MIMEText(html, 'html', 'utf-8')
    msg['From'] = _format_addr('DotDotGame <%s>' % from_addr)
    msg['To'] = _format_addr('用户 <%s>' % to_addr)
    msg['Subject'] = Header('您重置密码的请求……', 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    # server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()



