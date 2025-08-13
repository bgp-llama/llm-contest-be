from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel
from app.database import create_tables, SessionLocal
from app.routers import chatbots, chat
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from insert_mock import seed

load_dotenv()

agent = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    """애플리케이션 생명주기 관리"""
    create_tables()
    with SessionLocal() as db:
        # Mock 데이터 삽입
        seed(db)
    yield


# FastAPI 앱 생성
app = FastAPI(
    title="챗봇 플랫폼 API",
    description="AI 기반 챗봇 생성, 사용, 추천 플랫폼",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (업로드된 파일들)
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 라우터 등록
app.include_router(chatbots.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "챗봇 플랫폼 API에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


class MessageRequest(BaseModel):
    message: Optional[str] = None


class MessageResponse(BaseModel):
    response: str
    success: bool
    error: str = None


async def get_agent():
    """MCP 에이전트를 초기화하고 반환합니다."""
    global agent
    if agent is None:
        try:
            client = MultiServerMCPClient(
                {
                    "chatbot": {
                        "transport": "streamable_http",
                        "url": "http://localhost:8010/mcp/",
                    }
                }
            )
            tools = await client.get_tools()
            agent = create_react_agent("openai:gpt-4o-mini", tools)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"에이전트 초기화 실패: {str(e)}"
            )
    return agent


@app.post("/invoke", response_model=MessageResponse)
async def invoke(request: MessageRequest):
    """자연어 명령을 처리하고 응답을 반환합니다."""
    try:
        agent = await get_agent()
        # message 또는 messages 필드 사용
        user_message = request.message
        if not user_message:
            return MessageResponse(
                response="", success=False, error="메시지가 제공되지 않았습니다."
            )
        response = await agent.ainvoke({"messages": user_message})

        # 응답에서 마지막 메시지 추출
        last_message = (
            response["messages"][-1].content
            if response["messages"]
            else "응답이 없습니다."
        )

        return MessageResponse(response=last_message, success=True)
    except Exception as e:
        return MessageResponse(response="", success=False, error=str(e))
