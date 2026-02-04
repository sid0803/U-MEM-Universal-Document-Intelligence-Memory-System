import pdfplumber
from docx import Document
from PIL import Image
import pytesseract


def extract_text(file_path: str, file_type: str) -> str:
    try:
        if file_type == "pdf":
            return extract_text_from_pdf(file_path)

        elif file_type == "txt":
            return extract_text_from_txt(file_path)

        elif file_type == "docx":
            return extract_text_from_docx(file_path)

        elif file_type == "image":
            return extract_text_from_image(file_path)

        else:
            return ""

    except Exception as e:
        print("Text extraction failed:", e)
        return ""


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()


def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs).strip()


def extract_text_from_image(file_path: str) -> str:
    image = Image.open(file_path).convert("RGB")
    text = pytesseract.image_to_string(image)
    return text.strip()
