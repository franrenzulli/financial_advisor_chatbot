import os
import pytesseract

from pathlib import Path
from typing import List
from ibm_docprocessing import DocumentParser
from docx import Document
from PIL import Image


PDF_DIR = Path(__file__).resolve().parent.parent / "data" 
TXT_DIR = Path(__file__).resolve().parent.parent / "data" / "generated_texts"
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".jpg", ".jpeg", ".png"}

def extract_text(file_path: Path) -> str:
    ext = file_path.suffix.lower()

    if ext == ".pdf":
        parser = DocumentParser()
        result = parser.parse(file_path)
        return result.text

    elif ext in {".docx", ".doc"}:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])

    elif ext in {".jpg", ".jpeg", ".png"}:
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)

    else:
        raise ValueError(f"File type not supported: {ext}")

def load_from_folder() -> List[Path]:
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    generated_files = []

    for file_path in PDF_DIR.iterdir():
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            print(f"Ignored (extension not supported): {file_path.name}")
            continue

        print(f"Processing: {file_path.name}")
        try:
            text = extract_text(file_path)
            output_path = TXT_DIR / f"{file_path.stem}.txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            generated_files.append(output_path)
            print(f"✅ Saved at: {output_path.name}")
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")

    return generated_files

if __name__ == "__main__":
    txt_paths = load_from_folder()
    print(f"\n{len(txt_paths)} files generated.")
