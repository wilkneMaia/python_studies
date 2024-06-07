import os
import re
import fitz  # PyMuPDF
from PyPDF3 import PdfFileReader, PdfFileWriter


def create_directory(directory):
    """
    Creates a directory if it doesn't exist.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_pdf_range(input_pdf, start_page, end_page, output_pdf_path):
    """
    Saves a range of pages as a separate PDF.
    """
    pdf_writer = PdfFileWriter()
    for page in range(start_page, end_page + 1):
        pdf_writer.addPage(input_pdf.getPage(page))
    with open(output_pdf_path, 'wb') as output_pdf_file:
        pdf_writer.write(output_pdf_file)
    print(f"Saved PDF: {output_pdf_path}")


def process_pdf(input_pdf_path, output_folder, marker):
    """
    Processes the PDF to split documents based on the marker.
    """
    create_directory(output_folder)

    input_pdf_fitz = fitz.open(input_pdf_path)
    input_pdf_pypdf2 = PdfFileReader(input_pdf_path)

    current_page = 0
    start_page = 0

    while current_page < input_pdf_pypdf2.getNumPages():
        page = input_pdf_fitz.load_page(current_page)
        text = page.get_text("text")

        normalized_text = " ".join(text.split())
        print(
            f"Processing page {current_page}, normalized text: {normalized_text}")

        if marker in normalized_text and current_page != 0:
            end_page = current_page - 1

            output_pdf_path = os.path.join(
                output_folder, f'document_{start_page + 1}_to_{end_page + 1}.pdf')
            save_pdf_range(input_pdf_pypdf2, start_page,
                           end_page, output_pdf_path)

            start_page = current_page

        current_page += 1

    if start_page < input_pdf_pypdf2.getNumPages():
        output_pdf_path = os.path.join(
            output_folder, f'document_{start_page + 1}_to_{input_pdf_pypdf2.getNumPages()}.pdf')
        save_pdf_range(input_pdf_pypdf2, start_page,
                       input_pdf_pypdf2.getNumPages() - 1, output_pdf_path)


def main():
    input_pdf_path = 'OM_01.pdf'
    output_folder = 'output_pdfs'
    marker = "PERMISSÃO DE TRABALHO SEGURO"

    process_pdf(input_pdf_path, output_folder, marker)
    print(f'PDFs separados salvos em: {output_folder}')


if __name__ == "__main__":
    main()
