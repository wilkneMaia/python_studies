import os

import fitz  # PyMuPDF

from PyPDF3 import PdfFileReader
from PyPDF3 import PdfFileWriter

import pandas as pd


# Define the input and output paths
input_pdf_path = 'RIP SEMANA 23.pdf'
output_folder = 'output_pdfs'  # Output folder for the split PDFs
output_excel_path = 'output_data.xlsx'

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
    print(f"Saved PDF: {output_pdf_path}")

# Function to extract the "N° OM:" and "DESCRIÇÃO OM:" from the text


def extract_info(text):
    info = {}
    if "N° OM:" in text:
        start = text.find("N° OM:") + len("N° OM:")
        end = text.find("\n", start)
        if end == -1:
            end = len(text)
        info['N° OM'] = text[start:end].strip().split()[0]
    if "DESCRIÇÃO OM:" in text and "OBSERVAÇÕES:" in text:
        start = text.find("DESCRIÇÃO OM:") + len("DESCRIÇÃO OM:")
        end = text.find("OBSERVAÇÕES:", start)
        if end == -1:
            end = len(text)
        # Extract only the relevant description text
        description = text[start:end].strip()
        info['Descrição OM'] = description
    return info


# Initialize list to collect "N° OM" and "DESCRIÇÃO OM" information
info_list = []

# Loop through the PDF and split based on the pattern observed in the document
current_page = 0
start_page = 0
marker = "PERMISSÃO DE TRABALHO SEGURO"

while current_page < input_pdf_pypdf2.getNumPages():
    page = input_pdf_fitz.load_page(current_page)
    text = page.get_text("text")

    # Normalize the text
    normalized_text = " ".join(text.split())
    print(f"Page {current_page} text:\n{normalized_text}\n")
    print(
        f"Processing page {current_page}, found marker: {marker in normalized_text}")

    if marker in normalized_text and current_page != 0:
        end_page = current_page - 1

        # Extract info to use as file name
        page_start_text = input_pdf_fitz.load_page(start_page).get_text("text")
        normalized_start_text = " ".join(page_start_text.split())
        info = extract_info(normalized_start_text)
        if 'N° OM' in info:
            output_pdf_path = os.path.join(
                output_folder, f'{info["N° OM"]}.pdf')
            print(f"Saving PDF as {output_pdf_path}")
            save_pdf_range(input_pdf_pypdf2, start_page,
                           end_page, output_pdf_path)
            print(
                f"Saved {info['N° OM']}.pdf from page {start_page} to {end_page}")
            info_list.append(info)

        start_page = current_page

    current_page += 1

# Save the last document and extract info
if start_page < input_pdf_pypdf2.getNumPages():
    text = input_pdf_fitz.load_page(start_page).get_text("text")
    normalized_text = " ".join(text.split())
    info = extract_info(normalized_text)
    if 'N° OM' in info:
        output_pdf_path = os.path.join(output_folder, f'{info["N° OM"]}.pdf')
        print(f"Saving PDF as {output_pdf_path}")
        save_pdf_range(input_pdf_pypdf2, start_page,
                       input_pdf_pypdf2.getNumPages() - 1, output_pdf_path)
        print(
            f"Saved {info['N° OM']}.pdf from page {start_page} to {input_pdf_pypdf2.getNumPages() - 1}")
        info_list.append(info)

# Create a DataFrame and save to Excel
df = pd.DataFrame(info_list, columns=['N° OM', 'Descrição OM'])
df.to_excel(output_excel_path, index=False)

print(f'PDFs separados salvos em: {output_folder}')
print(f'Dados extraídos salvos em: {output_excel_path}')
