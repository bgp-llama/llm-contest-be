import asyncio
import httpx
from typing import List, Dict, Any
from fastmcp import FastMCP
import logging

# FastMCP 서버 초기화
mcp = FastMCP(
    name="Chatbot Server",
    instructions="이 서버는 챗봇을 제어할 수 있는 다양한 도구들을 제공합니다."
)

@mcp.tool()
async def get_proper_chatbot(message: str) -> str:
    """사용자 메시지를 분석하여 가장 적합한 챗봇의 ID를 반환합니다."""
    try:
        # FastAPI 서버에서 모든 챗봇 정보 가져오기
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/chatbots/all")
            if response.status_code != 200:
                return "챗봇 정보를 가져올 수 없습니다."
            
            chatbots = response.json()
            
            if not chatbots:
                return "사용 가능한 챗봇이 없습니다."
            
            # 챗봇 정보를 컨텍스트로 제공하여 LLM이 판단하도록 함
            context = f"""
사용자 메시지: {message}

사용 가능한 챗봇들:
{chr(10).join([f"- ID: {c['id']}, 설명: {c['description']}" for c in chatbots])}

중요: 위 챗봇 중에서 사용자 메시지와 가장 적합한 챗봇의 ID만 숫자로 반환하세요.

반드시 지켜야 할 규칙:
1. 숫자만 반환 (예: "1", "2", "3")
2. 따옴표 사용하지 않음
3. 설명이나 문장 추가하지 않음
4. "ID는", "입니다" 같은 표현 사용하지 않음
5. 오직 숫자만 반환

잘못된 예시:
- "적합한 챗봇 ID는 4입니다" ❌
- "ID: 4" ❌
- "4번 챗봇" ❌

올바른 예시:
- "4" ✅
- "1" ✅
- "2" ✅
"""
            
            return context
            
    except Exception as e:
        logging.error(f"챗봇 선택 중 오류 발생: {e}")
        return f"오류가 발생했습니다: {str(e)}"

if __name__ == "__main__":
    print("🚀 Chatbot MCP 서버 시작 (포트: 8010)")
    
    # streamable-http 모드로 서버 실행
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8010) 