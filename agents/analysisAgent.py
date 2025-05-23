from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from agents.tools import send_email, search, database, e2b_execute_python, generate_plan, \
    generate_report, plan_execute
from dotenv import load_dotenv
load_dotenv()

class AnalysisAgent:
    def __init__(self):
        self.model = ChatOpenAI(model='qwen-plus-latest', base_url='https://dashscope.aliyuncs.com/compatible-mode/v1')

    def create_email_assistant(self):
        email_assistant = create_react_agent(
            model=self.model,
            tools=[send_email],
            prompt="你是一个邮件发送助手，负责邮件发送",
            name="email_assistant"
        )
        return email_assistant

    def create_search_assistant(self):
        search_assistant = create_react_agent(
            model=self.model,
            tools=[search],
            prompt="你是一个搜索助手",
            name="search_assistant"
        )
        return search_assistant

    def create_database_assistant(self,db_type,db_user,db_pwd,db_address,db_name):
        database_assistant = create_react_agent(
            model=self.model,
            tools=database(self.model,db_type,db_user,db_pwd,db_address,db_name),
            prompt="""
                您是一个设计用于与SQL数据库交互的数据库助手。
                给定一个输入问题，创建一个语法正确的MYSQL查询来运行，然后查看查询结果并返回答案。
                您可以按相关列对结果进行排序，以返回数据库中最有趣的示例。
                永远不要查询特定表中的所有列，只询问给定问题的相关列。
                您可以访问与数据库交互的工具。
                仅使用以下工具。仅使用以下工具返回的信息来构建您的最终答案。
                在执行查询之前，您必须仔细检查查询。如果在执行查询时出错，请重写查询并重试。
                不要对数据库执行任何DML语句（INSERT、UPDATE、DELETE、DROP等）。
                首先，您应该始终查看数据库中的表，看看可以查询什么。
                请勿跳过此步骤。
                然后，您应该查询最相关表的模式。
                """,
            name='database_assistant'
        )
        return database_assistant

    def create_generate_plan_assistant(self):
        generate_plan_assistant=create_react_agent(
            model=self.model,
            tools=[generate_plan],
            prompt='你是计划生成助手，负责为excel文件或csv文件数据集生成分析计划',
            name='generate_plan_assistant'
        )
        return generate_plan_assistant

    def create_plan_execute_assistant(self):
        plan_execute_assistant = create_react_agent(
            model=self.model,
            tools=[plan_execute],
            prompt='你是计划执行助手，负责对计划进行执行',
            name='plan_execute_assistant'
        )
        return plan_execute_assistant

    def create_code_execute_assistant(self):
        code_execute_assistant = create_react_agent(
            model=self.model,
            tools=[e2b_execute_python],
            prompt='你是代码执行助手，如果没有代码请必须生成代码再执行，并且只能执行一次代码，'
                   '如果有生成图表代码那么必须将图表美化好看',
            # prompt='你是图表生成助手，负责生成Python代码并执行，如果没有图表代码请必须生成python图表代码再执行，而且必须将图表美化好看',
            name='code_execute_assistant'
        )
        return code_execute_assistant

    def create_generate_report_assistant(self):
        generate_report_assistant = create_react_agent(
            model=self.model,
            tools=[generate_report],
            prompt='你是报告生成助手，负责为数据分析报告的生成',
            name='generate_report_assistant'
        )
        return generate_report_assistant

    def create_workflow(
            self,
            email_assistant,
            search_assistant,
            database_assistant,
            # code_execute_assistant,
            generate_plan_assistant,
            plan_execute_assistant,
            report_assistant,
    ):
        workflow =create_supervisor(
            agents=[
                email_assistant,
                search_assistant,
                database_assistant,
                # code_execute_assistant,
                generate_plan_assistant,
                plan_execute_assistant,
                report_assistant
            ],
            model=self.model,
            prompt=(
                "你是数据分析助手,你管理着搜索助手,邮件发送助手,数据库助手,"
                "计划生成助手,计划执行助手,报告生成助手,并把工作分配给他们。"
            )
        ).compile()
        return workflow

    @staticmethod
    async def chat(workflow,content):
        res=await workflow.ainvoke({'messages':[{'role':'user','content':content}]})
        return res['messages'][-1].content

    async def run(self,content:str,user):
        email_assistant=self.create_email_assistant()
        search_assistant=self.create_search_assistant()
        code_execute_assistant=self.create_code_execute_assistant()
        generate_plan_assistant=self.create_generate_plan_assistant()
        plan_execute_assistant=self.create_plan_execute_assistant()
        report_assistant=self.create_generate_report_assistant()
        db_settings=user.configure

        """判断用户有没有配置数据库"""
        database_assistant=self.create_database_assistant(
            db_settings.db_type,
            db_settings.db_user,
            db_settings.db_pwd,
            db_settings.db_address,
            db_settings.db_name
        ) if db_settings else self.create_database_assistant(db_type=None,db_user=None,db_pwd=None,db_address=None,db_name=None)

        workflow = self.create_workflow(
            email_assistant,
            search_assistant,
            database_assistant,
            # code_execute_assistant,
            generate_plan_assistant,
            plan_execute_assistant,
            report_assistant
        )
        msg= await self.chat(workflow,content)
        return msg

# if __name__ == '__main__':
#     aa=AnalysisAgent()
#     aa.run(content='我想知道房屋表有哪些不同的区域,按照数量给我生成图表')