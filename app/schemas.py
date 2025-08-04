from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# User 스키마
class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Chatbot 스키마
class ChatbotBase(BaseModel):
    name: str
    description: Optional[str] = None
    model_name: str
    system_prompt: Optional[str] = None


class ChatbotCreate(ChatbotBase):
    pass


class Chatbot(ChatbotBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Document 스키마
class DocumentBase(BaseModel):
    filename: str
    file_type: str


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
    id: int
    file_path: str
    content: Optional[str] = None
    created_at: datetime
    chatbot_id: int

    class Config:
        from_attributes = True


# Conversation 스키마
class ConversationBase(BaseModel):
    title: str


class ConversationCreate(ConversationBase):
    chatbot_id: int


class Conversation(ConversationBase):
    id: int
    created_at: datetime
    chatbot_id: int

    class Config:
        from_attributes = True


# Message 스키마
class MessageBase(BaseModel):
    content: str
    role: str


class MessageCreate(MessageBase):
    conversation_id: int


class Message(MessageBase):
    id: int
    created_at: datetime
    conversation_id: int

    class Config:
        from_attributes = True


# Chat 스키마
class ChatRequest(BaseModel):
    message: str
    conversation_id: int


class ChatResponse(BaseModel):
    message: str
    conversation_id: int


# 추천 스키마
class RecommendationRequest(BaseModel):
    user_interests: List[str]
    use_case: str
    technical_level: str


class RecommendationResponse(BaseModel):
    recommended_chatbots: List[Chatbot]
    reasoning: str
