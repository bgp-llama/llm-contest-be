from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple

from app.database import get_db, Chatbot, Conversation, Message
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    Conversation as ConversationSchema,
    Message as MessageSchema,
)
from app.llm_service import LLMService

router = APIRouter(prefix="/chat", tags=["chat"])

llm_service = LLMService()


@router.post("/", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest, db: Session = Depends(get_db)):
    """챗봇과 대화"""
    try:
        # 대화 세션 조회
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == request.conversation_id)
            .first()
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="대화 세션을 찾을 수 없습니다")

        # 챗봇 조회
        chatbot = (
            db.query(Chatbot).filter(Chatbot.id == conversation.chatbot_id).first()
        )
        if not chatbot:
            raise HTTPException(status_code=404, detail="사용 가능한 챗봇이 없습니다")

        # 대화 기록 조회
        history = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
            .all()
        )
        history_tuples = build_history_tuples(history)

        # AI 응답 생성
        if chatbot.documents:
            # RAG 사용
            documents = [doc.content for doc in chatbot.documents]
            chain = await llm_service.create_rag_chain(documents, chatbot.model_name)
            response = await llm_service.chat_with_rag(
                request.message, chain, history_tuples, chatbot.system_prompt
            )
        else:
            # 일반 LLM 사용
            response = await llm_service.chat_with_llm(
                request.message,
                chatbot.system_prompt,
                history_tuples,
                chatbot.model_name,
            )
        # 사용자 메시지 저장
        user_message = Message(
            content=request.message, role="user", conversation_id=conversation.id
        )
        db.add(user_message)

        # AI 응답 저장
        ai_message = Message(
            content=response, role="assistant", conversation_id=conversation.id
        )
        db.add(ai_message)
        db.commit()

        return ChatResponse(message=response, conversation_id=conversation.id)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations", response_model=ConversationSchema)
async def create_conversation(
    conversation_data: ConversationCreate, db: Session = Depends(get_db)
):
    """새로운 대화 세션 생성"""
    try:
        db_conversation = Conversation(
            title=conversation_data.title,
            chatbot_id=conversation_data.chatbot_id,
        )
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        return db_conversation
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/conversations", response_model=List[ConversationSchema])
async def get_conversations(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """대화 세션 목록 조회"""
    conversations = db.query(Conversation).offset(skip).limit(limit).all()
    return conversations


@router.get(
    "/conversations/{conversation_id}/messages", response_model=List[MessageSchema]
)
async def get_conversation_messages(
    conversation_id: int, db: Session = Depends(get_db)
):
    """대화 세션의 메시지 목록 조회"""
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )
    return messages

    # @router.delete("/conversations/{conversation_id}")
    # async def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    #     """대화 세션 삭제"""
    #     conversation = (
    #         db.query(Conversation).filter(Conversation.id == conversation_id).first()
    #     )
    #     if not conversation:
    #         raise HTTPException(status_code=404, detail="대화 세션을 찾을 수 없습니다")

    #     db.delete(conversation)
    #     db.commit()

    #     return {"message": "대화 세션이 삭제되었습니다"}


def build_history_tuples(messages):
    history_tuples: List[Tuple[str, str]] = []
    pending_user: Optional[str] = None
    for msg in messages:
        if msg.role == "user":
            pending_user = msg.content
        elif msg.role == "assistant":
            if pending_user is not None:
                history_tuples.append((pending_user, msg.content))
                pending_user = None
            else:
                history_tuples.append(("", msg.content))
    return history_tuples
