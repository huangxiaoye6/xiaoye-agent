from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from .tools import search
from dotenv import load_dotenv
load_dotenv()

class AIChat:
    """普通AI聊天"""
    def __init__(self):
        self.model=ChatOpenAI(model='qwen2.5-coder-14b-instruct',base_url='https://dashscope.aliyuncs.com/compatible-mode/v1')
    @staticmethod
    def prompt():
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", '你是小耶AI助手,你的名字叫小耶AI'),
                ('human','{messages}')
            ]
        )
        return prompt_template

    async def chat(self,msg,prompt):
        agent=create_react_agent(model=self.model,tools=[search],prompt=prompt)
        res=agent.invoke({'messages':[HumanMessage(content=msg)]})
        if res['messages'][1].content == '':
            return res['messages'][-1].content
        else:
            return res['messages'][1].content

    async def run(self,msg):
        prompt_template=self.prompt()
        content=await self.chat(msg=msg,prompt=prompt_template)
        return content








