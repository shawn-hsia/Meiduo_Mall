
from itsdangerous import TimedJSONWebSignatureSerializer, BadData
from django.conf import settings
import logging
logger = logging.getLogger('django')



def generate_access_token(openid):
    # 序列化生成器的材料和初始化条件
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,
                                                 expires_in=600,)
    # 添加加密材料
    data = {"openid": openid}

    token = serializer.dumps(data)

    return token.decode()


# 对用户传回的token解密
def check_access_token(token):
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,
                                                 expires_in=600)
    try:
        data = serializer.loads(token)

    except BadData as e:
        logger.error(e)
        return None


    openid = data.get('openid')

    return openid
