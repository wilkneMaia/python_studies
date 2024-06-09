import json
import os
import re

import fitz  # PyMuPDF

from PyPDF3 import PdfFileReader
from PyPDF3 import PdfFileWriter

import pandas as pd


def create_directory(directory):
    """Creates a directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_pdf_range(input_pdf, start_page, end_page, output_pdf_path):
    """Saves a range of pages as a separate PDF."""
    pdf_writer = PdfFileWriter()
    for page in range(start_page, end_page + 1):
        pdf_writer.addPage(input_pdf.getPage(page))
    with open(output_pdf_path, 'wb') as output_pdf_file:
        pdf_writer.write(output_pdf_file)
    print(f"Saved PDF: {output_pdf_path}")


def save_to_excel(data, file_name):
    """Saves data to an Excel file."""
    df = pd.json_normalize(data)  # Flatten the JSON structure to a table
    df.to_excel(file_name, index=False)
    print(f"Data successfully saved to {file_name}")


def process_pdf(input_pdf_path, output_folder, marker):
    """Processes the PDF to split documents based on the marker."""
    create_directory(output_folder)
    input_pdf_fitz = fitz.open(input_pdf_path)
    input_pdf_pypdf2 = PdfFileReader(input_pdf_path)

    current_page = 0
    start_page = 0
    separated_texts = []

    while current_page < input_pdf_pypdf2.getNumPages():
        page = input_pdf_fitz.load_page(current_page)
        text = page.get_text("text")
        normalized_text = " ".join(text.split())

        if marker in normalized_text and current_page != 0:
            end_page = current_page - 1
            output_pdf_path = os.path.join(
                output_folder, f'document_{start_page + 1}_to_{end_page + 1}.pdf'
            )
            save_pdf_range(input_pdf_pypdf2, start_page,
                           end_page, output_pdf_path)

            description_fields = extract_description(output_pdf_path, 0)
            om = description_fields.get(
                "om", f"document_{start_page + 1}_to_{end_page + 1}")
            new_output_pdf_path = os.path.join(output_folder, f'{om}.pdf')
            os.rename(output_pdf_path, new_output_pdf_path)

            separated_texts.append((new_output_pdf_path, description_fields))

            start_page = current_page

        current_page += 1

    if start_page < input_pdf_pypdf2.getNumPages():
        output_pdf_path = os.path.join(
            output_folder, f'document_{start_page + 1}_to_{input_pdf_pypdf2.getNumPages()}.pdf'
        )
        save_pdf_range(input_pdf_pypdf2, start_page,
                       input_pdf_pypdf2.getNumPages() - 1, output_pdf_path)

        description_fields = extract_description(output_pdf_path, 0)
        om = description_fields.get(
            "om", f"document_{start_page + 1}_to_{input_pdf_pypdf2.getNumPages()}")
        new_output_pdf_path = os.path.join(output_folder, f'{om}.pdf')
        os.rename(output_pdf_path, new_output_pdf_path)

        separated_texts.append((new_output_pdf_path, description_fields))

    return separated_texts


def extract_description(file_path, page_number):
    """Extracts description fields from the PDF."""
    initial_data = "CENTRO EMITENTE:"
    final_data = "OBSERVAÇÕES:"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    if no_data(df):
        return {}

    try:
        extracted_fields = {
            "om": find_value_after_label(df, "N° OM:", 1),
            "issue_center": find_value_after_label(df, "CENTRO EMITENTE:", 1),
            "center_plant": find_value_after_label(df, "CENTRO/PLANTA:", 1),
            "om_description": find_value_after_label(df, "DESCRIÇÃO OM:", 1),
        }
        return extracted_fields

    except Exception as e:
        print(f"Error extracting fields: {e}")
        return {}


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


def no_data(df):
    """Checks if the DataFrame is empty."""
    if df is None or df.empty:
        print("No data to extract.")
        return True
    return False


def find_value_after_label(df, label, offset=1):
    """Finds the value in the DataFrame after a specific label."""
    try:
        index = df[df['line'].str.contains(label, case=False, na=False)].index
        if not index.empty:
            value_index = index[0] + offset
            if value_index < len(df):
                value = df.iloc[value_index]['line'].strip()
                return value
        return None
    except Exception as e:
        print(f"Error finding value after label {label}: {e}")
        return None


def verificar_texto_in(texto_maior, texto_especifico):
    return texto_especifico in texto_maior


def contains_om_number(text):
    # Define a expressão regular para corresponder 'OM' seguido por qualquer número
    pattern = r'OM \d+'
    # Use a função search do módulo re para procurar a expressão no texto
    match = re.search(pattern, text)
    # Retorne True se encontrar uma correspondência, caso contrário, False
    return bool(match)


def extract_equipment_fields(file_path, page_number):
    """
    Extracts equipment fields from the PDF.
    """
    initial_data = r'OM \d+'  # Regex to find initial data
    final_data = "ORDEM DE MANUTENÇÃO"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    if no_data(df):
        return {}

    try:
        # Inicializa os campos
        equipment_number = ""
        description_equipment = ""
        cost_center = ""
        criticality = ""
        installation_location = ""
        description_installation_location = ""
        upper_installation_location = ""
        description_upper_installation_location = ""
        equipment_characteristics = ""

        # Verifica o valor da terceira linha
        if len(df) > 2:
            first_line = df.iloc[0]['line'].strip()
            third_line = df.iloc[2]['line'].strip()

            if third_line == "EQUIPAMENTO":
                # if third_line != "EQUIPAMENTO" and verificar_texto_in(first_line, 'OM ') == True:
                cost_center = find_value_after_label(df, "Centro de Custo", 11)
                criticality = find_value_after_label(df, "Criticidade", 11)
                installation_location = find_value_after_label(
                    df, "Local de Instalação", 9)
                description_installation_location = find_value_after_label(
                    df, "Descrição do Local de Instalação", 9)
                upper_installation_location = find_value_after_label(
                    df, "Local de Instalação Superior", 7)
                description_upper_installation_location = find_value_after_label(
                    df, "Descrição do Local de Instalação Superior", 7)

            elif contains_om_number(first_line):
                equipment_number = find_value_after_label(df, "Número", 12)
                description_equipment = find_value_after_label(
                    df, "Descrição Equipamento", 1)
                cost_center = find_value_after_label(df, "Centro de Custo", 12)
                criticality = find_value_after_label(df, "Criticidade", 12)
                installation_location = find_value_after_label(
                    df, "Local de Instalação", 11)
                description_installation_location = find_value_after_label(
                    df, "Descrição do Local de Instalação", 11)
                upper_installation_location = find_value_after_label(
                    df, "Local de Instalação Superior", 9)
                description_upper_installation_location = find_value_after_label(
                    df, "Descrição do Local de Instalação Superior", 9)
                equipment_characteristics = find_value_after_label(
                    df, "Características do Equipamento", 9)

        # Coleta os campos restantes
        extracted_fields = {
            "equipment_number": equipment_number,
            "description_equipment": description_equipment,
            "cost_center": cost_center,
            "criticality": criticality,
            "installation_location": installation_location,
            "description_installation_location": description_installation_location,
            "upper_installation_location": upper_installation_location,
            "description_upper_installation_location": description_upper_installation_location,
            "equipment_characteristics": equipment_characteristics
        }

        return extracted_fields

    except Exception as e:
        print(f"Error extracting fields: {e}")
        return {}


# Função auxiliar find_value_after_label para encontrar valores após um rótulo específico
def find_value_after_label(df, label, offset=1):
    """Finds the value in the DataFrame after a specific label."""
    try:
        index = df[df['line'].str.contains(label, case=False, na=False)].index
        if not index.empty:
            value_index = index[0] + offset
            if value_index < len(df):
                value = df.iloc[value_index]['line'].strip()
                return value
        return None
    except Exception as e:
        print(f"Error finding value after label {label}: {e}")
        return None


def extract_maintenance_order_fields(file_path, page_number):
    """Extracts maintenance order fields from the PDF."""
    initial_data = "ORDEM DE MANUTENÇÃO"
    final_data = "NOTA DE MANUTENÇÃO"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    if no_data(df):
        return {}

    try:
        tem = "",
        plan_maintenance = "",
        plan_description = "",
        operation_condition = "",

        line = df.iloc[34]['line'].strip()
        line_2 = df.iloc[35]['line'].strip()

        tipo_manutencao = find_value_after_label(df, "Tipo de Manutenção", 18)
        tipo_atividade = find_value_after_label(df, "Tipo de Atividade", 18)

        if line == "Status Sistema Ordem":
            tem = find_value_after_label(df, "Equipe", 11)
            plan_maintenance = ""
            plan_description = ""
            operation_condition = find_value_after_label(
                df, "Condição de Operação", 12)
            print("Equipe: 1")
        elif line_2 == "Status Sistema Ordem":
            tem = find_value_after_label(df, "Equipe", 12)
            plan_maintenance = ""
            plan_description = ""
            operation_condition = find_value_after_label(
                df, "Condição de Operação", 12)
            print("Equipe: 2")

        else:
            tem = find_value_after_label(df, "Equipe", 14)
            plan_maintenance = find_value_after_label(
                df, "Plano de Manutenção", 16)
            plan_description = find_value_after_label(
                df, "Descrição do Plano", 16)
            operation_condition = find_value_after_label(
                df, "Condição de Operação", 14)
            print("Equipe: fim")

        if tipo_manutencao == "Manutenção Corretiva não Reparo":
            tipo_manutencao = "Manutenção Corretiva"
            tipo_atividade = "Reparo"

        extracted_fields = {
            "start_date": find_value_after_label(df, "Data Inicio", 21),
            "start_time": find_value_after_label(df, "Hora", 20),
            "end_date": find_value_after_label(df, "Data Fim", 19),
            "end_time": find_value_after_label(df, "Hora Fim", 19),
            "duration": find_value_after_label(df, "Duração", 19),
            "priority": find_value_after_label(df, "Prioridade", 18),
            "maintenance_type": tipo_manutencao,
            "activity_type": tipo_atividade,
            "starting_point": find_value_after_label(df, "Ponto de Partida", 4),
            "length": find_value_after_label(df, "Comprimento", 4),
            "plan_maintenance": plan_maintenance,
            "plan_description": plan_description,
            "operation_condition": operation_condition,
            "order_system_status": find_value_after_label(df, "Status Sistema Ordem", 2),
            "order_user_status": find_value_after_label(df, "Status Usuário Ordem", 2),
            "team": tem,
        }
        return extracted_fields

    except Exception as e:
        print(f"Error extracting fields: {e}")
        return {}


def combine_fields(description_fields, equipment_fields, order_fields):
    """Combines description, equipment, maintenance order, and maintenance note fields into a single dictionary."""
    combined_data = {
        "om": description_fields.get("om", ""),
        "issue_center": description_fields.get("issue_center", ""),
        "center_plant": description_fields.get("center_plant", ""),
        "om_description": description_fields.get("om_description", ""),
        "equipment_fields": equipment_fields,
        "order_fields": order_fields
        # **equipment_fields,
        # **order_fields,
    }
    return combined_data


def save_to_json(data, file_name):
    """Saves data to a JSON file."""
    try:
        with open(file_name, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {file_name}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")


def main():
    input_pdf_path = './pdf/combined_document.pdf'
    marker = "PERMISSÃO DE TRABALHO SEGURO"
    output_dir = "./output_pdfs"

    separated_texts = process_pdf(input_pdf_path, output_dir, marker)
    all_combined_data = []

    for idx, (file_path, description_fields) in enumerate(separated_texts):
        try:
            om = description_fields.get("om", f"document_{idx + 1}")
            equipment_fields = extract_equipment_fields(file_path, 1)
            order_fields = extract_maintenance_order_fields(file_path, 1)

            if om and equipment_fields and order_fields:
                combined_data = combine_fields(
                    description_fields, equipment_fields, order_fields
                )
                all_combined_data.append(combined_data)
            else:
                print(
                    f"Could not extract sufficient data for document {idx + 1}.")
        except Exception as e:
            print(f"Error processing document {idx + 1}: {e}")

    # Save all combined data to a single JSON file
    json_file_path = f"{output_dir}/combined_maintenance_data.json"
    save_to_json(all_combined_data, json_file_path)

    # Save all combined data to an Excel file
    excel_file_path = f"{output_dir}/combined_maintenance_data.xlsx"
    save_to_excel(all_combined_data, excel_file_path)


if __name__ == "__main__":
    main()
