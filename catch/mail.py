#coding:utf-8
#!/usr/bin/python

import smtplib
from email.mime.text import MIMEText
'''
SERVER_EMAIL = 'pachong321@163.com'
# Mailserver configuration
EMAIL_HOST = "smtp.163.com"
EMAIL_PORT = 25
EMAIL_HOST_USER='pachong321@163.com'
EMAIL_HOST_PASSWORD='pachong'
'''

#mailto_list=["526365272@qq.com", "xianglongit@163.com","dragonmar@163.com"]#此处设置 要接受通知邮件的邮箱地址
mailto_list=["dragonmar@163.com"]#此处设置 要接受通知邮件的邮箱地址
mail_host="smtp.163.com"  #设置服务器
mail_user="pachong321@163.com"    #用户名
mail_pass="pachong"   #口令
mail_postfix="163.com"  #发件箱的后缀

def send_mail(sub,content):  #to_list：收件人；sub：主题；content：邮件内容
    me="hello"+"<"+mail_user+"@"+mail_postfix+">"   #这里的hello可以任意设置，收到信后，将按照设置显示
    msg = MIMEText(content,_subtype='html',_charset='utf-8')    #创建一个实例，这里设置为html格式邮件
    msg['Subject'] = sub    #设置主题
    msg['From'] = me
    msg['To'] = ";".join(mailto_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)  #连接smtp服务器
        s.login(mail_user,mail_pass)  #登陆服务器
        s.sendmail(me, mailto_list, msg.as_string())  #发送邮件
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False
    """
if __name__ == '__main__':
    if send_mail(mailto_list,"这是一份资料，老张 请及时接受啊","老张 你是谁  老李什么时候会拉啊？"):
        print "success"
    else:
        print "fail"
    """
