from pydantic import BaseModel, EmailStr, Field, UUID4
from uuid import uuid4
from typing import Optional

class RegisterUser(BaseModel):
    password:str=Field(description='密码验证')
    phone:str=Field(description='手机号码验证',max_length=11,min_length=11,pattern=r'^\d{11}$')
    email:EmailStr=Field(description='邮箱验证')


class ADDUserConfigure(BaseModel):
    user_id:UUID4=Field(description='用户ID')
    db_type:Optional[str]=Field(description='数据库类型',max_length=64,default=None)
    db_address:Optional[str]=Field(description='数据库地址',max_length=64,default=None)
    db_name:Optional[str]=Field(description='数据库名称',max_length=64,default=None)
    db_user:Optional[str]=Field(description='数据库用户名',max_length=64,default=None)
    db_pwd:Optional[str]=Field(description='数据库密码',max_length=64,default=None)


class DBConnectionSchema(BaseModel):
    db_type:Optional[str]=Field(description='数据库类型',max_length=64,default=None)
    db_address:Optional[str]=Field(description='数据库地址',max_length=64,default=None)
    db_name:Optional[str]=Field(description='数据库名称',max_length=64,default=None)
    db_user:Optional[str]=Field(description='数据库用户名',max_length=64,default=None)
    db_pwd:Optional[str]=Field(description='数据库密码',max_length=64,default=None)


