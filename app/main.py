from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.database import create_tables
from app.routers import chatbots, chat

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """애플리케이션 생명주기 관리"""
    create_tables()
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
