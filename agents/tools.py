import base64
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Annotated, Optional, List
from e2b_code_interpreter import Sandbox
from fpdf import FPDF
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_experimental.utilities import PythonREPL
from langchain_openai import ChatOpenAI
import pandas as pd

from schemas.AgentSchema import EmailTemplateSchema, PythonExecuteSchema, PlanExecuteSchema, PlanGenerateSchema, \
    ReportSchema
from langchain_core.tools import tool
from pydantic import EmailStr
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from dotenv import load_dotenv
load_dotenv()

# 发送邮件工具
@tool(name_or_callable='send_email', return_direct=True, args_schema=EmailTemplateSchema)
def send_email(to: EmailStr, subject: str, content: str=None,img_file=None) -> str:
    """负责发送邮件，接收4个参数为：1、收件人邮箱，2、邮件主题，3、邮件文本内容：一般为数据分析的结论，
    4、邮件图片附件:为代码执行助手生成图表的路径"""
    try:
        msg = MIMEMultipart()
        if content is not None:
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            # msg.attach(MIMEText(content, 'html', 'utf-8'))
        if img_file is not None:
            img=MIMEImage(open('./media/ai_charts/{0}'.format(img_file), 'rb').read())
            img.add_header('content-type', 'image/octet-stream')
            img.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', img_file))
            msg.attach(img)
        msg['From'] = '17323814232@163.com'
        msg['To'] = to
        msg['Subject'] = subject
        server = smtplib.SMTP_SSL('smtp.163.com')
        server.connect('smtp.163.com', 465)
        server.login('17323814232@163.com', 'GAiBt5SMwqB35jGi')
        server.sendmail('17323814232@163.com', to, msg=msg.as_string())
        server.quit()
        print('邮件发送成功')
        return '向{0}发送邮件成功'.format(to)
    except Exception as e:
        print('邮件发送失败')
        return ('邮件发送失败！原因是{0}'.format(str(e)),)

# 搜索工具
search=TavilySearchResults(max_results=2)

# 数据集分析计划生成工具
@tool(name_or_callable='generate_plan',return_direct=True,args_schema=PlanGenerateSchema)
def generate_plan(file_name:str):
    """为excel或csv文件生成一份分析计划"""
    print(file_name)
    if file_name:
        try:
            df=pd.read_excel("./media/uploadFile/{0}".format(file_name),nrows=5)
            columns=df.columns
            model=ChatOpenAI(model='qwq-32b-preview', base_url='https://dashscope.aliyuncs.com/compatible-mode/v1')
            prompt=PromptTemplate.from_template('请用pandas和matplotlib或seaborn完成对{name}数据集的全方位、多维度的数据分析,'
                                                '它的字段为：{columns},数据的一部分是{data},只给出代码,不能给无关的内容')
            chain=prompt | model | StrOutputParser()
            result=chain.invoke({'name':file_name,'columns':columns,'data':df})
            print('计划生成成功')
            return ('计划生成成功：{0}'.format(result),)
        except Exception as e:
            return ('计划生成失败：{0}'.format(str(e)),)
    return ('计划生成失败：必须提供数据集的名字',)

@tool(name_or_callable='generate_report',return_direct=True,args_schema=ReportSchema)
def generate_report(img_names:List[str]):
    """负责报告的生成"""
    print('开始生成报告')
    pdf = FPDF()
    for image_name in img_names:
        print(image_name)
        pdf.add_page()
        page_width = pdf.w
        page_height = pdf.h
        try:
            pdf.image(image_name, x=10, y=10, w=page_width - 20)  # 左右边距各 10mm
        except Exception as e:
            # 若图片不存在或出错，添加错误提示
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Error loading image: {image_name}", ln=True, align="C")
            pdf.cell(0, 10, str(e), ln=True, align="C")
    pdf.output("report.pdf")
    return ('报告生成成功,名字为report.pdf',)

# 数据集分析计划执行工具
@tool(name_or_callable='plan_execute',return_direct=True,args_schema=PlanExecuteSchema)
def plan_execute(file_name:str,code:str,img_names:List[str]):
    """负责计划执行"""
    print(code)
    print('计划开始执行')
    with Sandbox() as sandbox:
        if file_name:
            code = code.replace(file_name, "/user/home/{0}".format(file_name))
            with open("./media/uploadFile/{0}".format(file_name), "rb") as file:
                sandbox.files.write("/user/home/{0}".format(file_name), file)
            if not sandbox.files.exists("/user/home/{0}".format(file_name)):
                print('文件上传失败')
                return ('任务完成，代码执行失败，输出为：沙箱环境上传文件失败}',)
            execution = sandbox.run_code(code)
            error = execution.error
            img = execution.results
            if error:
                execute_error = f'任务完成，代码执行失败，错误为：{execution.error.name}'
                print('代码执行错误', error)
                return execute_error
            elif len(img) != 0:
                print('开始生成图表')
                for i,name in zip(range(len(img)),img_names):
                    img_file_path = './media/ai_charts/{0}.png'.format(name)
                    with open(img_file_path, 'wb') as f:
                        f.write(base64.b64decode(img[i].png))
                        f.flush()  # 强制刷新缓冲区
                        os.fsync(f.fileno())  # 确保数据写入磁盘
                        time_out = 0
                        while time_out < 15:
                            if os.path.exists(img_file_path):
                                break
                            else:
                                time_out += 1
                    print('图表全部成功生成')
                return ('任务完成，计划执行成功',)
        return ('计划执行失败：必须提供数据集的名字',)

# 数据库未进行配置提示工具
@tool(return_direct=True)
def db_connection():
    """负责告诉大模型该用户没有配置数据库"""
    return '请告诉用户在小耶APP的设置里面配置数据库信息'

# 数据库配置是否存在判断函数
def database(model,db_type,db_user,db_pwd,db_address,db_name):
    try:
        db = SQLDatabase.from_uri("{0}+pymysql://{1}:{2}@{3}:3306/{4}".format(db_type,
        db_user,db_pwd,db_address,db_name))
        toolkit=SQLDatabaseToolkit(db=db, llm=model)
        tools = toolkit.get_tools()
        return tools
    except Exception as e:
        print(e)
        return [db_connection]

# 本地代码执行工具
@tool
def python_repl_tool(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """使用它来执行python代码，只能执行一次代码。如果你想看到一个值的输出，你应该用
    `print（…）`打印出来。这对用户是可见的。如果是输出是图片，保存格式为png，文件名必须要唯一不能重复。完成任务就停止执行该工具"""
    try:
        repl = PythonREPL()
        result = repl.run(code)
    except BaseException as e:
        return f"执行失败。错误: {repr(e)}"
    result_str = f'成功执行:\n```python\n{code}\n```\n标准输出: {result}'
    return (
        result_str
    )

# e2b沙箱环境工具
@tool(name_or_callable='execute_python_code',return_direct=True,args_schema=PythonExecuteSchema)
def e2b_execute_python(file_name:Optional[str],img_name:str,code: str):
    """负责执行python代码，只能执行一次代码。如果你想看到一个值的输出，你应该用
    `print（…）`打印出来。这对用户是可见的。如果生成图片就用img_name这个变量来保存，完成任务就停止执行该工具"""
    print('-----------------------------------------')
    # print(file_name)
    # print(img_name)
    with Sandbox() as sandbox:
        if file_name:
            code=code.replace(file_name,"/user/home/{0}".format(file_name))
            # print('上传前',sandbox.files.list(path='/home/user/'))
            with open("./media/uploadFile/{0}".format(file_name), "rb") as file:
                sandbox.files.write("/user/home/{0}".format(file_name), file)
            if not sandbox.files.exists("/user/home/{0}".format(file_name)):
                # print('文件上传失败')
                return ('任务完成，代码执行失败，输出为：沙箱环境上传文件失败}',)
        execution = sandbox.run_code(code)
        error=execution.error
        img = execution.results
        text=execution.logs.stdout
        if error:
            execute_error=f'任务完成，代码执行失败，错误为：{execution.error.name}'
            print('代码执行错误', error)
            return execute_error
        elif len(img)!=0:
            img_file_path='./media/ai_charts/{0}'.format(img_name)
            with open(img_file_path, 'wb') as f:
                f.write(base64.b64decode(img[0].png))
                f.flush()  # 强制刷新缓冲区
                os.fsync(f.fileno())  # 确保数据写入磁盘
                time_out = 0
                while time_out < 15:
                    if os.path.exists(img_file_path):
                        break
                    else:
                        time_out += 1
            print(f'图表成功生成,名字为{img_name}',)
            return (f'任务完成，代码执行成功，输出图表名字为为：{img_name}',)
        elif len(text)!=0:
            print('文本输出为：', text)
            return (f'任务完成，代码执行成功，输出为：{execution.logs.stdout}',)


