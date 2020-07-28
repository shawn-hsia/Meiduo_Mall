from meiduo_mall.libs.yuntongxun.ccp_sms import CCP

if __name__ == '__main__':
    CCP().send_template_sms('13896584883', ['测试验证码', 5], 1)