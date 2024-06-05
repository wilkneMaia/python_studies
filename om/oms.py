import os
import re

import fitz  # PyMuPDF

import pandas as pd


# Define the input and output paths
input_pdf_path = 'Ordens sistemáticas da BRITAGEM até 07.03.pdf'
output_excel_path = 'output_data.xlsx'

# Read the input PDF with PyMuPDF to extract text
input_pdf = fitz.open(input_pdf_path)

# Function to extract the relevant information from the text


def extract_info(text):
    info = {}
    # Using regex to extract all relevant fields
    patterns = {
        'N° OM': r'N° OM:\s*(\S+)',
        'Descrição OM': r'DESCRIÇÃO OM:\s*(.*?)\s*OBSERVAÇÕES:',
        'Número': r'Número\s*(\S+)',
        'Centro de Custo': r'Centro de Custo\s*(\S+)',
        'Criticidade': r'Criticidade\s*(\S+)',
        'Local de Instalação': r'Local de Instalação\s*(\S+)',
        'Descrição do Local de Instalação': r'Descrição do Local de Instalação\s*(.*?)\s*Local de Instalação Superior',
        'Local de Instalação Superior': r'Local de Instalação Superior\s*(\S+)',
        'Descrição do Local de Instalação Superior': r'Descrição do Local de Instalação Superior\s*(.*?)\s*Características do Equipamento',
        'Data Inicio': r'Data Inicio\s*(\d{2}/\d{2}/\d{4})',
        'Data Final': r'Data Fim\s*(\d{2}/\d{2}/\d{4})',
        'Hora Inicio': r'Hora Início\s*(\d{2}:\d{2})',
        'Hora Fim': r'Hora Fim\s*(\d{2}:\d{2})',
        'Duração (h)': r'Duração \(h\)\s*(\S+)',
        'Prioridade': r'Prioridade\s*(\S+)'
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            info[key] = match.group(1).strip()
    return info


# Initialize list to collect the extracted information
info_list = []

# Loop through the PDF and extract information based on the observed pattern in the document
for page_num in range(input_pdf.page_count):
    page = input_pdf.load_page(page_num)
    text = page.get_text("text")

    # Normalize the text
    normalized_text = " ".join(text.split())

    # Extract the info
    info = extract_info(normalized_text)

    # Add to the list if the extracted information is not empty
    if info:
        info_list.append(info)

# Create a DataFrame and save to Excel
if info_list:
    df = pd.DataFrame(info_list)
    df.to_excel(output_excel_path, index=False)
    print(f'Dados extraídos salvos em: {output_excel_path}')
else:
    print("No information extracted to save in Excel")

print(f'PDF processing completed.')


# import os
# import re

# import pdfplumber

# import pandas as pd


# # Define the input and output paths
# input_pdf_path = 'OMS.pdf'
# output_folder = 'output_pdfs'  # Output folder for the split PDFs
# output_excel_path = 'output_data.xlsx'

# # Define the output folder and create it if it doesn't exist
# os.makedirs(output_folder, exist_ok=True)

# # Function to save a range of pages as a separate PDF


# def save_pdf_range(pdf, start_page, end_page, output_pdf_path):
#     with pdfplumber.open(input_pdf_path) as pdf:
#         pages = [pdf.pages[i] for i in range(start_page, end_page + 1)]
#         with pdfplumber.open(output_pdf_path, 'w') as new_pdf:
#             new_pdf.add_pages(pages)
#     print(f"Saved PDF: {output_pdf_path}")

# # Function to extract information from the text


# def extract_info(text):
#     info = {}
#     # Using regex to extract "N° OM:"
#     om_match = re.search(r'N° OM:\s*(\S+)', text)
#     if om_match:
#         try:
#             info['N° OM'] = int(om_match.group(1))
#         except ValueError:
#             info['N° OM'] = om_match.group(1)

#     # Using regex to extract "DESCRIÇÃO OM:"
#     desc_match = re.search(
#         r'DESCRIÇÃO OM:\s*(.*?)\s*OBSERVAÇÕES:', text, re.DOTALL)
#     if desc_match:
#         info['Descrição OM'] = desc_match.group(1).strip()

#     # Extract fields for "Centro de Custo", "Criticidade", "Local de Instalação", "Descrição do Local de Instalação", "Local de Instalação Superior", and "Descrição do Local de Instalação Superior"
#     loc_match = re.search(
#         r'Centro de Custo\s*(\S+)\s*Criticidade\s*(\S+)\s*Local de Instalação\s*(\S+)\s*Descrição do Local de Instalação\s*(.*?)\s*Local de Instalação Superior\s*(\S+)\s*Descrição do Local de Instalação Superior\s*(.*?)\s*(?:\s*[\r\n]+|$)', text, re.DOTALL)
#     if loc_match:
#         try:
#             info['Centro de Custo'] = int(loc_match.group(1))
#         except ValueError:
#             info['Centro de Custo'] = loc_match.group(1)
#         info['Criticidade'] = loc_match.group(2)
#         info['Local de Instalação'] = loc_match.group(3)
#         info['Descrição do Local de Instalação'] = loc_match.group(
#             4).strip().split('\n')[0]
#         info['Local de Instalação Superior'] = loc_match.group(5)
#         info['Descrição do Local de Instalação Superior'] = loc_match.group(
#             6).strip().split('\n')[0]

#     # Using regex to extract "Data Inicio", "Data Final", and "Prioridade"
#     data_inicio_match = re.search(
#         r'Planejador\s*(\d{2}/\d{2}/\d{4})\s*(\d{2}:\d{2})\s*(\d{2}/\d{2}/\d{4})\s*(\d{2}:\d{2})\s*(\d+\.\d+)\s*(\S+)', text)
#     if data_inicio_match:
#         info['Data Inicio'] = data_inicio_match.group(1)
#         info['Data Final'] = data_inicio_match.group(3)
#         info['Prioridade'] = data_inicio_match.group(6)

#     return info


# # Initialize list to collect the extracted information
# info_list = []

# # Open the PDF file with pdfplumber
# with pdfplumber.open(input_pdf_path) as pdf:
#     current_page = 0
#     start_page = 0
#     marker = "PERMISSÃO DE TRABALHO SEGURO"

#     while current_page < len(pdf.pages):
#         page = pdf.pages[current_page]
#         text = page.extract_text()

#         # Normalize the text
#         normalized_text = " ".join(text.split())

#         if marker in normalized_text and current_page != 0:
#             end_page = current_page - 1

#             # Extract info to use as file name
#             section_text = ""
#             for page_num in range(start_page, end_page + 1):
#                 section_text += " " + pdf.pages[page_num].extract_text()

#             print(f"Extracting info from pages {start_page} to {end_page}")
#             info = extract_info(section_text)
#             print(f"Extracted info: {info}")

#             if 'N° OM' in info:
#                 output_pdf_path = os.path.join(
#                     output_folder, f'{info["N° OM"]}.pdf')
#                 save_pdf_range(pdf, start_page, end_page, output_pdf_path)
#                 info_list.append(info)
#             else:
#                 print("N° OM not found in section text")

#             start_page = current_page

#         current_page += 1

#     # Save the last document and extract info
#     if start_page < len(pdf.pages):
#         section_text = ""
#         for page_num in range(start_page, len(pdf.pages)):
#             section_text += " " + pdf.pages[page_num].extract_text()

#         print(
#             f"Extracting info from pages {start_page} to {len(pdf.pages) - 1}")
#         info = extract_info(section_text)
#         print(f"Extracted info: {info}")

#         if 'N° OM' in info:
#             output_pdf_path = os.path.join(
#                 output_folder, f'{info["N° OM"]}.pdf')
#             save_pdf_range(pdf, start_page, len(
#                 pdf.pages) - 1, output_pdf_path)
#             info_list.append(info)
#         else:
#             print("N° OM not found in section text")

# # Print the extracted info for "202402645957"
# for item in info_list:
#     if item['N° OM'] == 202402645957:
#         print(item)

# # Create a DataFrame and save to Excel
# if info_list:
#     df = pd.DataFrame(info_list, columns=[
#         'N° OM', 'Descrição OM', 'Centro de Custo', 'Criticidade', 'Local de Instalação', 'Descrição do Local de Instalação', 'Local de Instalação Superior', 'Descrição do Local de Instalação Superior', 'Data Inicio', 'Data Final', 'Prioridade'])
#     df.to_excel(output_excel_path, index=False)
#     print(f'Dados extraídos salvos em: {output_excel_path}')
# else:
#     print("No information extracted to save in Excel")

# print(f'PDFs separados salvos em: {output_folder}')
