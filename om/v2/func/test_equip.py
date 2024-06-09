import re

import fitz  # PyMuPDF

import pandas as pd


def contains_om_number(text):
    # Define a expressão regular para corresponder 'OM' seguido por qualquer número
    pattern = r'OM \d+'
    # Use a função search do módulo re para procurar a expressão no texto
    match = re.search(pattern, text)
    # Retorne True se encontrar uma correspondência, caso contrário, False
    return bool(match)


def extract_maintenance_order_data(file_path, page_number, initial_data_regex, final_data):
    """Extracts maintenance order data from the PDF between initial_data_regex and final_data sections."""
    try:
        pdf_document = fitz.open(file_path)

        if page_number < 0 or page_number >= pdf_document.page_count:
            print(
                f"Page {page_number} does not exist in the document. The document has {pdf_document.page_count} pages.")
            return None

        page = pdf_document.load_page(page_number)
        page_text = page.get_text()

        # Use regex to find the initial data matching the provided regex
        initial_data_match = re.search(initial_data_regex, page_text)
        if not initial_data_match:
            print(
                f"Initial data matching regex '{initial_data_regex}' not found.")
            return None

        initial_data = initial_data_match.group()
        order_start = page_text.find(initial_data)
        note_start = page_text.find(final_data)

        if order_start == -1 or note_start == -1:
            print(
                f"Sections {initial_data} and/or {final_data} were not found on the page.")
            return None

        order_data = page_text[order_start:note_start].strip()
        lines = order_data.split('\n')
        df = pd.DataFrame(lines, columns=['line'])

        return df

    except Exception as e:
        print(f"Error opening file: {e}")
        return None


def extract_equipment_fields(file_path, page_number):
    """
    Extracts equipment fields from the PDF.
    """
    initial_data = r'OM \d+'  # Regex to find initial data
    final_data = "ORDEM DE MANUTENÇÃO"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    # Verifica o valor das linhas
    if len(df) > 2:
        first_line = df.iloc[0]['line'].strip()
        third_line = df.iloc[2]['line'].strip()

        # Condição para retornar DataFrame quando terceira linha é "EQUIPAMENTO"
        if third_line == "EQUIPAMENTO":
            return df
        # Condição para não retornar DataFrame quando a terceira linha não é "EQUIPAMENTO"
        elif contains_om_number(first_line):
            print(
                f"Não foi possível encontrar os campos de equipamento na página {page_number}")
            return None


if __name__ == '__main__':
    # Define the path to the PDF file
    file_path = '../pdf/202304493693_ok.pdf'
    # Define the page number to extract the data
    page_number = 1

    # Extract the equipment fields from the PDF
    equipment_fields = extract_equipment_fields(file_path, page_number)
    if equipment_fields is not None:
        print(equipment_fields)
    else:
        print("No equipment fields were found.")
