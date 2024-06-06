import json
import re

import fitz  # PyMuPDF

import pandas as pd


def separate_documents(input_pdf_path, start_keyword, end_keyword):
    """
    Separa documentos dentro de um PDF com base em palavras-chave de início e fim.

    :param input_pdf_path: Caminho para o arquivo PDF
    :param start_keyword: Palavra-chave que marca o início de um documento
    :param end_keyword: Palavra-chave que marca o fim de um documento
    :return: Lista de textos dos documentos separados
    """
    input_pdf = fitz.open(input_pdf_path)
    separated_texts = []

    for page_num in range(input_pdf.page_count):
        page = input_pdf.load_page(page_num)
        text = page.get_text("text")
        start_index = text.find(start_keyword)
        end_index = text.find(end_keyword) + len(end_keyword)

        if start_index != -1 and end_index != -1:
            document_text = text[start_index:end_index].strip()
            separated_texts.append(document_text)

    return separated_texts


def extract_info(relevant_text, numero_om):
    """
    Extract information from the relevant text.
    """
    # Define regex patterns
    numero_pattern = re.compile(r"\b\d{8}\b")  # 8-digit numbers
    centro_custo_pattern = re.compile(r"\b\d{7}\b")  # 7-digit numbers

    # Find all matches
    numero_matches = numero_pattern.findall(relevant_text)
    centro_custo_matches = centro_custo_pattern.findall(relevant_text)

    # Extract "Descrição Equipamento"
    descricao_equipamento_match = re.search(
        r"Descrição Equipamento\s*(.*?)\s*EQUIPAMENTO", relevant_text, re.DOTALL)
    descricao_equipamento = descricao_equipamento_match.group(
        1).strip() if descricao_equipamento_match else ""

    # Split the text into lines to manually extract other fields
    lines = relevant_text.split('\n')

    combined_data = []
    max_length = max(len(numero_matches), len(centro_custo_matches))
    for i in range(max_length):
        num = numero_matches[i] if i < len(numero_matches) else ""
        cc = centro_custo_matches[i] if i < len(centro_custo_matches) else ""

        caracteristicas_equipamento = lines[20].strip() if len(
            lines) > 20 else ""
        if caracteristicas_equipamento == "ORDEM DE MANUTENÇÃO":
            caracteristicas_equipamento = ""

        combined_data.append({
            "tipo": "equipamento",
            "numero_om": numero_om,
            "numero": num,
            "descricao_equipamento": descricao_equipamento,
            "centro_custo": cc,
            "tipo_contador": "",
            "identificacao_tecnica": lines[14].strip() if len(lines) > 14 else "",
            "local_instalacao": lines[16].strip() if len(lines) > 16 else "",
            "descricao_local_instalacao": lines[17].strip() if len(lines) > 17 else "",
            "Local_instalação_superior": lines[18].strip() if len(lines) > 18 else "",
            "descrição_local_instalacao_superior": lines[19].strip() if len(lines) > 19 else "",
            "caracteristicas_equipamento": caracteristicas_equipamento
        })

    return combined_data


def save_to_excel(data, output_excel_path):
    """
    Save the extracted data to an Excel file.
    """
    df = pd.json_normalize(data, 'equipamento')
    df.to_excel(output_excel_path, index=False)
    print(f'Data extracted and saved to {output_excel_path}')


def main():
    """
    Main function to process the PDF and extract information.
    """
    # Define the input PDF path
    input_pdf_path = './pdf/OM_01.pdf'
    start_keyword = "Descrição Equipamento"
    end_keyword = "ORDEM DE MANUTENÇÃO"

    # Separate documents within the PDF
    separated_texts = separate_documents(
        input_pdf_path, start_keyword, end_keyword)

    found_texts = []
    numero_om = None
    for text in separated_texts:
        relevant_text = text

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

    # Remove duplicates based on all fields except 'tipo'
    unique_data = []
    seen = set()
    for data in extracted_data:
        data_tuple = tuple(data.items())
        if data_tuple not in seen:
            seen.add(data_tuple)
            unique_data.append(data)

    # Wrap the extracted data in the "equipamento" key
    output_data = [{"equipamento": unique_data}]

    # Save the data to a JSON file
    output_json_path = 'output_info.json'
    with open(output_json_path, 'w', encoding='utf-8') as file:
        json.dump(output_data, file, indent=4, ensure_ascii=False)

    print(f'Data extracted and saved to {output_json_path}')

    # Save the data to an Excel file
    output_excel_path = 'output_info.xlsx'
    save_to_excel(output_data, output_excel_path)


if __name__ == "__main__":
    main()
