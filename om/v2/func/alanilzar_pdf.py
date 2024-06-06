import fitz  # PyMuPDF

def extract_first_page_text(pdf_path):
    pdf_document = fitz.open(pdf_path)
    first_page = pdf_document.load_page(0)
    text = first_page.get_text("text")
    return text


pdf_path = './pdf/OM_00.pdf'
first_page_text = extract_first_page_text(pdf_path)
print(first_page_text)
