from fastapi import APIRouter
from starlette.responses import StreamingResponse

from agents.ai_chat import AIChat
ai=APIRouter()

@ai.get(path='/aiChat')
async def ai_chat(msg:str):
    aiChat=AIChat()
    content=await aiChat.run(msg=msg)
    return StreamingResponse(content)