from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from PIL import Image
class EmailTemplateSchema(BaseModel):
    to:EmailStr=Field(description='收件邮箱地址')
    subject:Optional[str]=Field(description='邮件主题',default=None)
    content:Optional[str]=Field(description='邮件文本内容',default=None)
    img_file:Optional[str]=Field(description='邮件图片名字',default=None)

class PythonExecuteSchema(BaseModel):
    code:Optional[str]=Field(description='Python代码')
    img_name:Optional[str]=Field(description='图片名字')
    file_name:Optional[str]=Field(description='文件名字')

class PlanGenerateSchema(BaseModel):
    file_name: str=Field(description='数据集的名字')

class PlanExecuteSchema(BaseModel):
    file_name: str=Field(description='数据集的名字')
    code:str=Field(description='代码')
    img_names:List[str]=Field(description='保存图片的名字')

class ReportSchema(BaseModel):
    img_names:List[str]=Field(description='保存图片的名字')