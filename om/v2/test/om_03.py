import json
import re

import fitz  # PyMuPDF


# Define the input PDF path
input_pdf_path = 'OM_00.pdf'

# Read the input PDF with PyMuPDF
input_pdf = fitz.open(input_pdf_path)

# Function to check if the specified text range is present


def check_text_range(text):
    start_keyword = "Descrição Equipamento"
    end_keyword = "ORDEM DE MANUTENÇÃO"

    if start_keyword in text and end_keyword in text:
        # Extract the text between the start and end keywords
        start_index = text.index(start_keyword)
        end_index = text.index(end_keyword) + len(end_keyword)
        relevant_text = text[start_index:end_index].strip()
        return relevant_text
    return None

# Function to extract information from the relevant text


def extract_info(relevant_text):
    # Define regex patterns
    numero_pattern = re.compile(r"\b\d{8}\b")  # 8-digit numbers
    centro_custo_pattern = re.compile(r"\b\d{7}\b")  # 7-digit numbers
    criticidade_pattern = re.compile(r"\b[A-Z]\b")  # Single uppercase letters
    tipo_contador_pattern = re.compile(
        r"Tipo Contador\s*(.*?)\s*Nº Identificação Técnica", re.DOTALL)
    termino_garantia_pattern = re.compile(
        r"Término da Garantia\s*(.*?)\s*Fonte radioativa", re.DOTALL)

    # Find all matches
    numero_matches = numero_pattern.findall(relevant_text)
    centro_custo_matches = centro_custo_pattern.findall(relevant_text)
    criticidade_matches = criticidade_pattern.findall(relevant_text)
    tipo_contador_matches = tipo_contador_pattern.findall(relevant_text)
    termino_garantia_matches = termino_garantia_pattern.findall(relevant_text)

    # Extract "Descrição Equipamento"
    descricao_equipamento_match = re.search(
        r"Descrição Equipamento\s*(.*?)\s*EQUIPAMENTO", relevant_text, re.DOTALL)
    descricao_equipamento = descricao_equipamento_match.group(
        1).strip() if descricao_equipamento_match else ""

    # Extract "Tipo Contador"
    tipo_contador = tipo_contador_matches[0].strip(
    ) if tipo_contador_matches else ""

    # Extract "Término da Garantia"
    termino_garantia = termino_garantia_matches[0].strip(
    ) if termino_garantia_matches else ""

    # Combine the results
    combined_data = []
    max_length = max(len(centro_custo_matches), len(criticidade_matches))
    for i in range(max_length):
        num = numero_matches[i] if i < len(numero_matches) else ""
        cc = centro_custo_matches[i] if i < len(centro_custo_matches) else ""
        crit = criticidade_matches[i] if i < len(criticidade_matches) else ""
        combined_data.append({
            "numero": num,
            "descricao_equipamento": descricao_equipamento,
            "centro_custo": cc,
            "criticidade": crit,
            "tipo_contador": tipo_contador,
            "termino_garantia": termino_garantia
        })

    return combined_data


# Loop through the pages in the PDF and check for the text range
found_texts = []
for page_num in range(input_pdf.page_count):
    page = input_pdf.load_page(page_num)
    text = page.get_text("text")

    relevant_text = check_text_range(text)
    if relevant_text:
        found_texts.append(relevant_text)

# Extract information from the found texts
extracted_data = []
for text in found_texts:
    extracted_data.extend(extract_info(text))

# Save the data to a JSON file
output_json_path = 'output_info.json'
with open(output_json_path, 'w', encoding='utf-8') as file:
    json.dump(extracted_data, file, indent=4, ensure_ascii=False)

print(f'Data extracted and saved to {output_json_path}')
