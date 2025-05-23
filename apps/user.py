from uuid import uuid4
import aiomysql
import aioredis
from fastapi import Body, Query, Depends, UploadFile, Form
from passlib.hash import bcrypt
from fastapi.routing import APIRouter
from pydantic import EmailStr,UUID4
from tortoise.exceptions import IntegrityError
from tortoise.expressions import Q
from schemas.UserSchema import RegisterUser,ADDUserConfigure,DBConnectionSchema
from models.UserModel import User, UserConfigure, UserUploadFile
from fastapi.responses import JSONResponse
from settings import success_code,creat_error_code,search_error_code,error_code
from utils.auth import create_token
from celery_task.task import celery_send_email
from random import randint
import aiofiles
from dependencies.UserDepends import get_redis_depend
user=APIRouter()

@user.post(path='/register',summary='用户注册')
async def user_register(data: RegisterUser,email_code:str=Query(),redis:aioredis.Redis=Depends(get_redis_depend)):
    data_dict=data.model_dump()
    data_dict['uuid']=str(uuid4())
    data_dict['password']=bcrypt.hash(data_dict['password'])
    phone=data_dict.get('phone')
    email=data_dict.get('email')
    code=await redis.get(data_dict['email'])
    if email_code==code:
        user_queryset=await User.filter(Q(phone=phone)|Q(email=email)).exists()
        if user_queryset:
            return {'msg':'注册失败','error':'用户已经存在','code':creat_error_code}
        else:
            try:
                await User.create(**data_dict)
                return {'msg':'注册成功','code':success_code}
            except Exception as e:
                return {'msg':'注册失败','error':str(e),'code':creat_error_code}
    elif code is None:
        return {'msg':'注册失败','error':'验证码已经过期','code':creat_error_code}
    else:
        return {'msg':'注册失败','error':'验证码错误','code':creat_error_code}

@user.post(path='/login',summary='用户密码登录')
async def user_login(username:str=Body(),password:str=Body()):
    user_queryset=None
    if len(username)==11:
        user_queryset=await User.get_or_none(phone=username)
    else:
        user_queryset = await User.get_or_none(email=username)
    if user_queryset:
        if bcrypt.verify(password,user_queryset.password):
            data={
                'phone':user_queryset.phone,
                'email':user_queryset.email,
            }
            token=create_token(data)
            return JSONResponse(content={'msg':'登录成功','code':success_code},headers={'Access-Token':token})
        else:
            return {'msg': '登录失败', 'error': '密码错误', 'code': search_error_code}
    else:
        return {'msg':'登录失败','error':'用户不存在','code':search_error_code}


@user.post(path='/sendEmail',summary='邮箱注册验证码')
async def send_email(email_to:EmailStr=Body(),redis:aioredis.Redis=Depends(get_redis_depend)):
    code=randint(100000,999999)
    await redis.setex(name=email_to,time=60,value=code)
    content = '你的验证码为：{0}，该验证码5分钟内有效，请勿泄露于他人！'.format(code)
    try:
        celery_send_email.delay(email_to,'用户注册',content)
        return {'msg':'邮件发送成功','code':success_code}
    except Exception as e:
        return {'msg':'邮件发送失败','error':str(e),'code':error_code}


@user.post(path='/userConfigure',summary='用户数据库信息配置')
async def user_configure(data:ADDUserConfigure):
    data_dict=data.model_dump()
    user=await User.exists(uuid=data_dict['user_id'])
    if user:
        user_configure_queryset=await UserConfigure.exists(user_id=data_dict['user_id'])
        if user_configure_queryset:
            try:
                await UserConfigure.filter(user_id=data_dict['user_id']).update(**data_dict)
                return {'msg': '修改成功', 'code': success_code}
            except Exception as e:
                return {'msg': '修改失败', 'error': str(e), 'code': creat_error_code}
        else:
            try:
                await UserConfigure.create(**data_dict)
                return {'msg':'添加成功','code':success_code}
            except Exception as e:
                return {'msg':'添加失败','error':str(e),'code':creat_error_code}
    return {'msg':'添加失败','error':'用户不存在','code':creat_error_code}

@user.post(path='/DBConnection',summary='测试数据库连接')
async def db_connect(data: DBConnectionSchema):
    data_dict=data.model_dump()
    db_address=data_dict.get('db_address')
    db_type=data_dict.get('db_type')
    db_name=data_dict.get('db_name')
    db_user=data_dict.get('db_user')
    db_pwd=data_dict.get('db_pwd')
    if db_type=='mysql':
        try:
            connect=await aiomysql.connect(host=db_address,port=3306,user=db_user,password=db_pwd,db=db_name)
            connect.close()
            return {'msg':'数据库连接成功','code':success_code}
        except Exception as e:
            return {'msg':'数据库连接失败','error':str(e),'code':error_code}

@user.post(path='/uploadFile',summary='文件上传')
async def upload_file(file:UploadFile,user_id:UUID4=Form(description='用户的标识')):
    file_name=file.filename
    file_type=file_name.split('.')[-1]
    allow_type=['xlsx','xls','csv']
    if file_type in allow_type:
        try:
            await UserUploadFile.create(user_id=user_id,file_name=file_name)
            async with aiofiles.open('./media/uploadFile/{0}'.format(file_name), 'wb') as f:
                await f.write(await file.read())
            return {'msg': '上传成功', 'code': success_code}
        except IntegrityError as e:
            return {'msg':'上传失败','error':f'用户身份异常,{str(e)}','code':error_code}
        except Exception as e:
            return {'msg':'上传失败','error':str(e),'code':error_code}
    return {'msg':'上传失败','error':'不支持上传{0}文件类型'.format(file_type),'code':error_code}









