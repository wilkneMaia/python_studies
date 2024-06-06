import json
import re

import fitz  # PyMuPDF

import pandas as pd


# Define the input PDF path
input_pdf_path = './pdf/OM_01.pdf'


def check_text_range(text):
    """
    Check if the specified text range is present and extract relevant text.
    """
    start_keyword = "Descrição Equipamento"
    end_keyword = "ORDEM DE MANUTENÇÃO"

    if start_keyword in text and end_keyword in text:
        start_index = text.index(start_keyword)
        end_index = text.index(end_keyword) + len(end_keyword)
        return text[start_index:end_index].strip()
    return None


def extract_info(relevant_text, numero_om):
    """
    Extract information from the relevant text.
    """
    # Define regex patterns
    numero_pattern = re.compile(r"\b\d{8}\b")  # 8-digit numbers
    centro_custo_pattern = re.compile(r"\b\d{7}\b")  # 7-digit numbers
    criticidade_pattern = re.compile(r"\b[A-Z]\b")  # Single uppercase letters

    # Find all matches
    numero_matches = numero_pattern.findall(relevant_text)
    centro_custo_matches = centro_custo_pattern.findall(relevant_text)
    criticidade_matches = criticidade_pattern.findall(relevant_text)

    # Extract "Descrição Equipamento"
    descricao_equipamento_match = re.search(
        r"Descrição Equipamento\s*(.*?)\s*EQUIPAMENTO", relevant_text, re.DOTALL)
    descricao_equipamento = descricao_equipamento_match.group(
        1).strip() if descricao_equipamento_match else ""

    # Split the text into lines to manually extract other fields
    lines = relevant_text.split('\n')

    combined_data = []
    max_length = max(len(numero_matches), len(
        centro_custo_matches), len(criticidade_matches))
    for i in range(max_length):
        num = numero_matches[i] if i < len(numero_matches) else ""
        cc = centro_custo_matches[i] if i < len(centro_custo_matches) else ""
        crit = criticidade_matches[i] if i < len(criticidade_matches) else ""

        combined_data.append({
            "numero_om": numero_om,
            "numero": num,
            "descricao_equipamento": descricao_equipamento,
            "centro_custo": cc,
            "criticidade": crit,
            "tipo_contador": "",
            "local_instalacao": lines[16].strip() if len(lines) > 16 else ""
        })

    return combined_data


def save_to_excel(data, output_excel_path):
    """
    Save the extracted data to an Excel file.
    """
    df = pd.DataFrame(data)
    df.to_excel(output_excel_path, index=False)
    print(f'Data extracted and saved to {output_excel_path}')


def main():
    """
    Main function to process the PDF and extract information.
    """
    # Read the input PDF with PyMuPDF
    input_pdf = fitz.open(input_pdf_path)

    # Loop through the pages in the PDF and check for the text range
    found_texts = []
    numero_om = None
    for page_num in range(input_pdf.page_count):
        page = input_pdf.load_page(page_num)
        text = page.get_text("text")
        relevant_text = check_text_range(text)

        # Extract "N° OM" from the text
        om_match = re.search(r"N° OM:\s*(\d{12})", text)
        if om_match:
            numero_om = om_match.group(1)

        if relevant_text:
            found_texts.append((relevant_text, numero_om))

    # Extract information from the found texts
    extracted_data = []
    for text, om in found_texts:
        extracted_data.extend(extract_info(text, om))

    # Save the data to a JSON file
    output_json_path = 'output_info.json'
    with open(output_json_path, 'w', encoding='utf-8') as file:
        json.dump(extracted_data, file, indent=4, ensure_ascii=False)

    print(f'Data extracted and saved to {output_json_path}')

    # Save the data to an Excel file
    output_excel_path = 'output_info.xlsx'
    save_to_excel(extracted_data, output_excel_path)


if __name__ == "__main__":
    main()
