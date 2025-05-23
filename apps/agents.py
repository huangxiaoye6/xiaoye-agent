from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from agents.analysisAgent import AnalysisAgent
from models.UserModel import User
from settings import ai_agent_error, error_code

agents=APIRouter()


@agents.get(path='/analyseAgent',summary='数据分析智能体')
async def get_analyse_agent(msg:str,phone:str):
    """
    :param msg:
    :param phone:
    :return:
    """
    user=await User.filter(phone=phone).select_related('configure').first()
    if user:
        try:
            agent=AnalysisAgent()
            content=await agent.run(content=msg,user=user)
            return StreamingResponse(content=content)
        except Exception as e:
            return {'msg':'请求失败','error':str(e),'code':ai_agent_error}
    else:
        return {'msg':'请求失败','error':'非法请求','code':error_code}






