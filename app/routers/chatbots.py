from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db, Chatbot, Document
from app.schemas import (
    ChatbotCreate,
    Chatbot as ChatbotSchema,
    McpChatbot,
    Document as DocumentSchema,
)
from app.file_processor import FileProcessor

router = APIRouter(prefix="/chatbots", tags=["chatbots"])


@router.post("/", response_model=ChatbotSchema)
async def create_chatbot(
    chatbot_data: str = Form(...),
    file: Optional[UploadFile] = None,
    db: Session = Depends(get_db),
):

    try:
        chatbot_data: ChatbotCreate = ChatbotCreate.model_validate_json(chatbot_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"chatbot_data parsing error: {e}")

    """새로운 챗봇 생성"""
    try:
        db_chatbot = Chatbot(
            name=chatbot_data.name,
            description=chatbot_data.description,
            model_name=chatbot_data.model_name,
            system_prompt=chatbot_data.system_prompt,
        )
        db.add(db_chatbot)
        db.commit()
        db.refresh(db_chatbot)

        # 파일이 업로드된 경우 문서 처리
        if file:
            # 파일 저장
            file_path, file_type = await FileProcessor.save_uploaded_file(file)

            # 텍스트 추출
            content = await FileProcessor.process_file(file_path, file_type)

            if not content:
                raise HTTPException(
                    status_code=400, detail="파일에서 텍스트를 추출할 수 없습니다"
                )

            # 문서 저장
            db_document = Document(
                filename=file.filename,
                file_path=file_path,
                file_type=file_type,
                content=content,
                chatbot_id=db_chatbot.id,
            )

            db.add(db_document)
            db.commit()

        return db_chatbot
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ChatbotSchema])
async def get_chatbots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """모든 챗봇 조회"""
    chatbots = db.query(Chatbot).offset(skip).limit(limit).all()
    return chatbots

@router.get("/all", response_model=List[McpChatbot])
async def get_mcp_chatbots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """모든 챗봇 조회"""
    chatbots = db.query(Chatbot).offset(skip).limit(limit).all()
    return [McpChatbot(id=chatbot.id, description=chatbot.description) for chatbot in chatbots]

@router.get("/{chatbot_id}", response_model=ChatbotSchema)
async def get_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    """특정 챗봇 조회"""
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="챗봇을 찾을 수 없습니다")
    return chatbot


# @router.post("/{chatbot_id}/documents")
# async def upload_document(
#     chatbot_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
# ):
#     """챗봇에 문서 업로드 (RAG용)"""
#     # 챗봇 존재 확인
#     chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
#     if not chatbot:
#         raise HTTPException(status_code=404, detail="챗봇을 찾을 수 없습니다")

#     # 파일 저장
#     file_path, file_type = await FileProcessor.save_uploaded_file(file)

#     # 텍스트 추출
#     content = await FileProcessor.process_file(file_path, file_type)

#     if not content:
#         raise HTTPException(
#             status_code=400, detail="파일에서 텍스트를 추출할 수 없습니다"
#         )

#     # 문서 저장
#     db_document = Document(
#         filename=file.filename,
#         file_path=file_path,
#         file_type=file_type,
#         content=content,
#         chatbot_id=chatbot_id,
#     )

#     db.add(db_document)
#     db.commit()
#     db.refresh(db_document)

#     return {
#         "message": "문서가 성공적으로 업로드되었습니다",
#         "document_id": db_document.id,
#     }


@router.get("/{chatbot_id}/documents", response_model=List[DocumentSchema])
async def get_chatbot_documents(chatbot_id: int, db: Session = Depends(get_db)):
    """챗봇의 문서 목록 조회"""
    documents = db.query(Document).filter(Document.chatbot_id == chatbot_id).all()
    return documents


# @router.delete("/{chatbot_id}")
# async def delete_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
#     """챗봇 삭제"""
#     chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
#     if not chatbot:
#         raise HTTPException(status_code=404, detail="챗봇을 찾을 수 없습니다")

#     db.delete(chatbot)
#     db.commit()

#     return {"message": "챗봇이 삭제되었습니다"}
