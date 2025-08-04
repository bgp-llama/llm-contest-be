from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# 데이터베이스 URL 설정
DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# 데이터베이스 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    model_name = Column(String)  # OpenAI 모델명
    system_prompt = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="chatbot")
    conversations = relationship("Conversation", back_populates="chatbot")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    file_type = Column(String)  # pdf, docx, hwp
    content = Column(Text)  # 추출된 텍스트
    created_at = Column(DateTime, default=datetime.utcnow)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"))

    chatbot = relationship("Chatbot", back_populates="documents")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"))

    chatbot = relationship("Chatbot", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    role = Column(String)  # user, assistant
    created_at = Column(DateTime, default=datetime.utcnow)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))

    conversation = relationship("Conversation", back_populates="messages")


# 데이터베이스 테이블 생성
def create_tables():
    Base.metadata.create_all(bind=engine)
