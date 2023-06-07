# ---------------
# Opening a PDF File
# ---------------

from pathlib import Path

from pypdf import PdfReader

pdf_path = (
    Path.cwd().parent
    / "practice_files"
    / "Pride_and_Prejudice.pdf"
)

pdf_reader = PdfReader(pdf_path)

# print(len(pdf_reader.pages))

# print(pdf_reader.metadata)

# print(pdf_reader.metadata.title)


# ---------------------------
# Extracting Text From a Page
# ---------------------------

first_page = pdf_reader.pages[0]

# print(type(first_page))

# print(first_page.extract_text())

for page in pdf_reader.pages:
    print(page.extract_text())


# -----------------------
# Putting It All Together
# -----------------------
