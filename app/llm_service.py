import os
import asyncio
from typing import List, Optional, Tuple
import inspect

from openai import OpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

    async def chat_with_llm(
        self,
        message: str,
        system_prompt: str,
        chat_history: List[Tuple[str, str]],
        model: str,
    ) -> str:
        try:
            messages = []

            # 시스템 프롬프트 추가
            messages.append({"role": "system", "content": system_prompt})

            # 채팅 히스토리 추가
            for user_msg, assistant_msg in chat_history:
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": assistant_msg})

            # 현재 메시지 추가
            messages.append({"role": "user", "content": message})

            def sync_call():
                return self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                )

            response = await asyncio.to_thread(sync_call)
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM 대화 오류: {e}")
            return "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."

    async def create_rag_chain(
        self,
        documents: List[str],
        model: str,
    ) -> ConversationalRetrievalChain:
        if not documents:
            raise ValueError("문서 리스트가 비어있습니다.")

        try:
            combined_text = "\n\n".join(documents)
            if not combined_text.strip():
                raise ValueError("결합된 텍스트가 비어있습니다.")

            texts = self.text_splitter.split_text(combined_text)
            if not texts:
                raise ValueError("텍스트 분할 결과가 비어있습니다.")

            vectorstore = FAISS.from_texts(texts, self.embeddings)
            llm = ChatOpenAI(model=model, temperature=0.5)

            chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=vectorstore.as_retriever(),
                return_source_documents=True,
            )

            return chain
        except Exception as e:
            print(f"RAG 체인 생성 오류: {e}")
            raise RuntimeError(f"RAG 체인 생성에 실패했습니다: {str(e)}")

    async def chat_with_rag(
        self,
        message: str,
        chain,
        chat_history: List[Tuple[str, str]],
        system_prompt: str,
    ) -> str:
        try:
            composed_question = f"{system_prompt}\n\n현재 질문 : {message}"

            payload = {
                "question": composed_question,
                "chat_history": chat_history,
            }

            if hasattr(chain, "invoke"):
                result = chain.invoke(payload)
                if inspect.isawaitable(result):
                    result = await result
            else:
                result = await asyncio.to_thread(lambda: chain(payload))

            response = result.get("answer", "")

            return response
        except Exception as e:
            print(f"RAG 대화 오류: {e}")
            return "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
