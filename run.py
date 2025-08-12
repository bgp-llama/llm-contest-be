#!/usr/bin/env python3
"""
챗봇 플랫폼 실행 스크립트
"""

import uvicorn
import os
import subprocess
import time
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

if __name__ == "__main__":
    print("🚀 챗봇 플랫폼 시작 중...")
    
    # MCP 서버 백그라운드로 실행
    print("🚀 MCP 서버 시작 중...")
    mcp_process = subprocess.Popen([
        "python", 
        "mcp/server/chatbot_server.py"
    ])
    
    # 잠시 대기
    print("⏳ MCP 서버 시작 대기 중...")
    time.sleep(3)
    
    try:
        # FastAPI 서버 실행
        print("🚀 FastAPI 서버 시작 중...")
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 서버들을 종료합니다...")
    finally:
        # MCP 프로세스 종료
        mcp_process.terminate()
        print("✅ MCP 서버 종료됨")
        print("✅ 모든 서버가 종료되었습니다.") 