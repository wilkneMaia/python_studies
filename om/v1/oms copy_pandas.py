import os
import re

import fitz  # PyMuPDF

import pandas as pd


# Define the input and output paths
input_pdf_path = 'OM_01.pdf'
output_folder = 'output_pdfs'  # Output folder for the split PDFs
output_excel_path = 'output_data.xlsx'

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Read the input PDF with PyMuPDF to extract text
input_pdf_fitz = fitz.open(input_pdf_path)

# Function to save a range of pages as a separate PDF


def save_pdf_range(input_pdf, start_page, end_page, output_pdf_path):
    pdf_writer = fitz.open()  # Create a new PDF in memory
    for page in range(start_page, end_page + 1):
        pdf_writer.insert_pdf(input_pdf, from_page=page, to_page=page)
    pdf_writer.save(output_pdf_path)
    pdf_writer.close()
    print(f"Saved PDF: {output_pdf_path}")

# Function to extract information from the text


def extract_info(text):
    info = {}

    # Extract "N° OM:"
    om_match = re.search(r'N° OM:\s*(\S+)', text)
    if om_match:
        try:
            info['N° OM'] = int(om_match.group(1))
        except ValueError:
            info['N° OM'] = om_match.group(1)

    # Extract "DESCRIÇÃO OM:"
    desc_match = re.search(
        r'DESCRIÇÃO OM:\s*(.*?)\s*OBSERVAÇÕES:', text, re.DOTALL)
    if desc_match:
        info['Descrição OM'] = desc_match.group(1).strip()

    # Extract fields for "Centro de Custo", "Criticidade", "Local de Instalação", "Descrição do Local de Instalação", "Local de Instalação Superior", and "Descrição do Local de Instalação Superior"
    loc_match = re.search(
        r'Número\s+(\S+)\s+Centro de Custo\s+(\S+)\s+Criticidade\s+(\S+)\s+Local de Instalação\s+(\S+)\s+Descrição do Local de Instalação\s+(.*?)\s+Local de Instalação Superior\s+(\S+)\s+Descrição do Local de Instalação Superior\s+(.*?)\s*(?:\s*[\r\n]+|$)', text, re.DOTALL)
    if loc_match:
        try:
            info['Centro de Custo'] = int(loc_match.group(2))
        except ValueError:
            info['Centro de Custo'] = loc_match.group(2)
        info['Criticidade'] = loc_match.group(3)
        info['Local de Instalação'] = loc_match.group(4)
        info['Descrição do Local de Instalação'] = loc_match.group(
            5).strip().split('\n')[0]
        info['Local de Instalação Superior'] = loc_match.group(6)
        info['Descrição do Local de Instalação Superior'] = loc_match.group(
            7).strip().split('\n')[0]

    # Extract "Data Inicio", "Data Final", and "Prioridade"
    data_inicio_match = re.search(
        r'Planejador\s*(\d{2}/\d{2}/\d{4})\s*(\d{2}:\d{2})\s*(\d{2}/\d{2}/\d{4})\s*(\d{2}:\d{2})\s*(\d+\.\d+)\s*(\S+)', text)
    if data_inicio_match:
        info['Data Inicio'] = data_inicio_match.group(1)
        info['Data Final'] = data_inicio_match.group(3)
        info['Prioridade'] = data_inicio_match.group(6)

    return info


# Initialize list to collect the extracted information
info_list = []

# Loop through the PDF and split based on the pattern observed in the document
current_page = 0
start_page = 0
marker = "PERMISSÃO DE TRABALHO SEGURO"

while current_page < input_pdf_fitz.page_count:
    page = input_pdf_fitz.load_page(current_page)
    text = page.get_text("text")

    # Normalize the text
    normalized_text = " ".join(text.split())

    if marker in normalized_text and current_page != 0:
        end_page = current_page - 1

        # Extract info to use as file name
        section_text = ""
        for page_num in range(start_page, end_page + 1):
            page = input_pdf_fitz.load_page(page_num)
            section_text += " " + page.get_text("text")

        info = extract_info(section_text)

        if 'N° OM' in info:
            output_pdf_path = os.path.join(
                output_folder, f'{info["N° OM"]}.pdf')
            save_pdf_range(input_pdf_fitz, start_page,
                           end_page, output_pdf_path)
            info_list.append(info)

        start_page = current_page

    current_page += 1

# Save the last document and extract info
if start_page < input_pdf_fitz.page_count:
    section_text = ""
    for page_num in range(start_page, input_pdf_fitz.page_count):
        page = input_pdf_fitz.load_page(page_num)
        section_text += " " + page.get_text("text")

    info = extract_info(section_text)

    if 'N° OM' in info:
        output_pdf_path = os.path.join(output_folder, f'{info["N° OM"]}.pdf')
        save_pdf_range(input_pdf_fitz, start_page,
                       input_pdf_fitz.page_count - 1, output_pdf_path)
        info_list.append(info)

# Create a DataFrame and save to Excel
if info_list:
    df = pd.DataFrame(info_list, columns=[
        'N° OM', 'Descrição OM', 'Centro de Custo', 'Criticidade', 'Local de Instalação', 'Descrição do Local de Instalação',
        'Local de Instalação Superior', 'Descrição do Local de Instalação Superior', 'Data Inicio', 'Data Final', 'Prioridade'])
    df.to_excel(output_excel_path, index=False)
    print(f'Dados extraídos salvos em: {output_excel_path}')
else:
    print("No information extracted to save in Excel")

print(f'PDFs separados salvos em: {output_folder}')