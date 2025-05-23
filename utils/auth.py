import jwt
from jwt import exceptions
import datetime
from settings import SECRET_KEY
from fastapi import HTTPException

def create_token(payload):
    salt =SECRET_KEY
    headers = {
        'typ': 'jwt',
        'alg': 'HS256',
    }
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    token = jwt.encode(payload=payload, key=salt, headers=headers, algorithm='HS256')
    return token

def authenticate(token):
    if token:
        salt =SECRET_KEY
        payload = None
        try:
            payload = jwt.decode(token, salt, algorithms='HS256', verify=True)
            return payload
        except exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=200,detail={'code': '1000', 'error': 'token已经失效,请重新登录'})
        except jwt.DecodeError:
            raise HTTPException(status_code=200,detail={'code': '1001', 'error': 'token认证失败'})
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=200,detail={'code': '1002', 'error': '非法的token'})
    else:
        raise HTTPException(status_code=200,detail={'code': '1003', 'error': '没有获取到token'})