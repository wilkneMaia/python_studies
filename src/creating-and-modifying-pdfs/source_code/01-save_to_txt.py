from pathlib import Path

from pypdf import PdfReader

pdf_path = (
    Path.cwd().parent
    / "practice_files"
    / "Pride_and_Prejudice.pdf"
)

pdf_reader = PdfReader(pdf_path)
text_file = Path.cwd() / "Pride_and_Prejudice.txt"

content = [
    f'{pdf_reader.metadata.title}',
    f'Number of pages: {len(pdf_reader.pages)}'
]

for page in pdf_reader.pages:
    content.append(page.extract_text())

text_file.write_text('\n'.join(content))
