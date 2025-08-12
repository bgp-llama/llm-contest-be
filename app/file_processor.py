import os
import PyPDF2
from docx import Document as DocxDocument
from typing import Optional, Tuple
import aiofiles
import tempfile


class FileProcessor:
    """파일 처리 클래스 - PDF, DOCX, HWP 파일에서 텍스트 추출"""

    @staticmethod
    async def extract_text_from_pdf(file_path: str) -> Optional[str]:
        """PDF 파일에서 텍스트 추출"""
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            print(f"PDF 텍스트 추출 오류: {e}")
            return None

    @staticmethod
    async def extract_text_from_docx(file_path: str) -> Optional[str]:
        """DOCX 파일에서 텍스트 추출"""
        try:
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"DOCX 텍스트 추출 오류: {e}")
            return None

    @staticmethod
    async def process_file(file_path: str, file_type: str) -> Optional[str]:
        """파일 타입에 따라 적절한 텍스트 추출 메서드 호출"""
        if file_type.lower() == "pdf":
            return await FileProcessor.extract_text_from_pdf(file_path)
        elif file_type.lower() == "docx":
            return await FileProcessor.extract_text_from_docx(file_path)
        else:
            print(f"지원하지 않는 파일 타입: {file_type}")
            return None

    @staticmethod
    async def save_uploaded_file(
        upload_file, upload_dir: str = "uploads"
    ) -> Tuple[str, str]:
        """업로드된 파일을 저장하고 파일 경로와 타입 반환"""
        # 업로드 디렉토리 생성
        os.makedirs(upload_dir, exist_ok=True)

        # 파일 확장자 확인
        file_extension = os.path.splitext(upload_file.filename)[1].lower()

        # 파일 타입 매핑
        file_type_map = {".pdf": "pdf", ".docx": "docx"}

        file_type = file_type_map.get(file_extension, "unknown")

        # 고유한 파일명 생성
        import uuid

        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)

        # 파일 저장
        async with aiofiles.open(file_path, "wb") as f:
            content = await upload_file.read()
            await f.write(content)

        return file_path, file_type
