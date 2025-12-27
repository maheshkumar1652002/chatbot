import fitz  # PyMuPDF
import sys
sys.stdout.reconfigure(encoding='utf-8')

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])
