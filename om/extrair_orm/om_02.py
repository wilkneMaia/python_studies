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

# Function to extract "Centro de Custo" and "Criticidade" from the relevant text


def extract_centro_custo_and_criticidade(relevant_text):
    # Define regex patterns
    centro_custo_pattern = re.compile(r"\b\d{7}\b")  # 7-digit numbers
    criticidade_pattern = re.compile(r"\b[A-Z]\b")  # Single uppercase letters

    # Find all matches
    centro_custo_matches = centro_custo_pattern.findall(relevant_text)
    criticidade_matches = criticidade_pattern.findall(relevant_text)

    # Combine the results
    combined_data = []
    for cc, crit in zip(centro_custo_matches, criticidade_matches):
        combined_data.append({"centro_custo": cc, "criticidade": crit})

    return combined_data


# Loop through the pages in the PDF and check for the text range
found_texts = []
for page_num in range(input_pdf.page_count):
    page = input_pdf.load_page(page_num)
    text = page.get_text("text")

    relevant_text = check_text_range(text)
    if relevant_text:
        found_texts.append(relevant_text)

# Extract "Centro de Custo" and "Criticidade" values from the found texts
extracted_data = []
for text in found_texts:
    extracted_data.extend(extract_centro_custo_and_criticidade(text))

# Save the data to a JSON file
output_json_path = 'output_centro_custo_criticidade.json'
with open(output_json_path, 'w', encoding='utf-8') as file:
    json.dump(extracted_data, file, indent=4, ensure_ascii=False)

print(f'Data extracted and saved to {output_json_path}')
