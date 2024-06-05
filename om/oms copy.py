import os

import fitz  # PyMuPDF

from PyPDF3 import PdfFileReader
from PyPDF3 import PdfFileWriter


# Define the input and output paths
input_pdf_path = 'RIP SEMANA 23.pdf'
output_folder = 'output_pdfs'  # Output folder for the split PDFs

# Define the output folder and create it if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Read the input PDF with PyMuPDF to extract text
input_pdf_fitz = fitz.open(input_pdf_path)

# Read the input PDF with PyPDF2 to manipulate pages
input_pdf_pypdf2 = PdfFileReader(input_pdf_path)

# Function to save a range of pages as a separate PDF


def save_pdf_range(input_pdf, start_page, end_page, output_pdf_path):
    pdf_writer = PdfFileWriter()
    for page in range(start_page, end_page + 1):
        pdf_writer.addPage(input_pdf.getPage(page))
    with open(output_pdf_path, 'wb') as output_pdf_file:
        pdf_writer.write(output_pdf_file)


# Loop through the PDF and split based on the pattern observed in the document
current_page = 0
file_counter = 1
start_page = 0
marker = "PERMISSÃO DE TRABALHO SEGURO"

while current_page < input_pdf_pypdf2.getNumPages():
    page = input_pdf_fitz.load_page(current_page)
    text = page.get_text()

    # Normalize the text
    normalized_text = " ".join(text.split())
    print(f"Page {current_page} text:\n{normalized_text}\n")
    print(
        f"Processing page {current_page}, found marker: {marker in normalized_text}")

    if marker in normalized_text and current_page != 0:
        print(f"New document found at page {current_page}")
        end_page = current_page - 1
        output_pdf_path = os.path.join(
            output_folder, f'split_document_{file_counter}.pdf')
        save_pdf_range(input_pdf_pypdf2, start_page, end_page, output_pdf_path)
        print(
            f"Saved split_document_{file_counter}.pdf from page {start_page} to {end_page}")
        start_page = current_page
        file_counter += 1

    current_page += 1

# Save the last document
if start_page < input_pdf_pypdf2.getNumPages():
    output_pdf_path = os.path.join(
        output_folder, f'split_document_{file_counter}.pdf')
    save_pdf_range(input_pdf_pypdf2, start_page,
                   input_pdf_pypdf2.getNumPages() - 1, output_pdf_path)
    print(
        f"Saved split_document_{file_counter}.pdf from page {start_page} to {input_pdf_pypdf2.getNumPages() - 1}")

print(f'PDFs separados salvos em: {output_folder}')
