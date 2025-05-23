from tortoise import Model,fields
from tortoise.fields import CASCADE


class User(Model):
    uuid=fields.UUIDField(description='唯一标识',primary_key=True)
    password=fields.CharField(description='密码',max_length=128)
    phone=fields.CharField(description='手机号码',max_length=11)
    email=fields.CharField(description='邮箱',max_length=64)
    create_time=fields.DatetimeField(description='创建时间',auto_now_add=True)
    is_delete=fields.BooleanField(description='是否删除',default=False)
    class Meta:
        table='user'
        table_description='用户表'

class UserConfigure(Model):
    user=fields.OneToOneField(model_name='models.User',on_delete=CASCADE,related_name='configure')
    db_type=fields.CharField(description='数据库类型',max_length=64,null=True)
    db_address=fields.CharField(description='数据库地址',max_length=64,null=True)
    db_name=fields.CharField(description='数据库名',max_length=64,null=True)
    db_user=fields.CharField(description='数据库用户名',max_length=64,null=True)
    db_pwd=fields.CharField(description='数据库密码',max_length=64,null=True)
    class Meta:
        table='UserConfigure'
        table_description='用户的数据库配置表'


class UserUploadFile(Model):
    user=fields.ForeignKeyField(model_name='models.User',on_delete=CASCADE,related_name='uploadFile')
    file_name=fields.CharField(description='文件名字',max_length=64,null=True)
    upload_time=fields.DatetimeField(description='上传时间',auto_now_add=True)
    class Meta:
        table='UserUploadFile'
        table_description='用户上传文件表'



