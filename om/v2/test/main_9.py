import json
import os
import re

import fitz  # PyMuPDF

import pandas as pd


def create_directory(directory):
    """Creates a directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_pdf_range(input_pdf, start_page, end_page, output_pdf_path):
    """Saves a range of pages as a separate PDF."""
    pdf_writer = fitz.open()
    for page_num in range(start_page, end_page + 1):
        pdf_writer.insert_pdf(input_pdf, from_page=page_num, to_page=page_num)
    pdf_writer.save(output_pdf_path)
    print(f"Saved PDF: {output_pdf_path}")


def save_to_excel(data, file_name):
    """Saves data to an Excel file."""
    df = pd.json_normalize(data)  # Flatten the JSON structure to a table
    df.to_excel(file_name, index=False)
    print(f"Data successfully saved to {file_name}")


def process_pdf(input_pdf_path, output_folder, marker):
    """Processes the PDF to split documents based on the marker."""
    create_directory(output_folder)
    input_pdf = fitz.open(input_pdf_path)
    current_page = 0
    start_page = 0
    separated_texts = []

    while current_page < input_pdf.page_count:
        page = input_pdf.load_page(current_page)
        text = page.get_text("text")
        normalized_text = " ".join(text.split())

        if marker in normalized_text and current_page != 0:
            end_page = current_page - 1
            output_pdf_path = os.path.join(
                output_folder, f'document_{start_page + 1}_to_{end_page + 1}.pdf')
            save_pdf_range(input_pdf, start_page, end_page, output_pdf_path)

            description_fields = extract_description(output_pdf_path, 0)
            om = description_fields.get(
                "om", f"document_{start_page + 1}_to_{end_page + 1}")
            new_output_pdf_path = os.path.join(output_folder, f'{om}.pdf')
            os.rename(output_pdf_path, new_output_pdf_path)

            separated_texts.append((new_output_pdf_path, description_fields))
            start_page = current_page

        current_page += 1

    if start_page < input_pdf.page_count:
        output_pdf_path = os.path.join(
            output_folder, f'document_{start_page + 1}_to_{input_pdf.page_count}.pdf')
        save_pdf_range(input_pdf, start_page,
                       input_pdf.page_count - 1, output_pdf_path)

        description_fields = extract_description(output_pdf_path, 0)
        om = description_fields.get(
            "om", f"document_{start_page + 1}_to_{input_pdf.page_count}")
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


def extract_maintenance_order_data(file_path, page_number, initial_data, final_data):
    """Extracts maintenance order data from the PDF between initial_data and final_data sections."""
    try:
        pdf_document = fitz.open(file_path)

        if page_number < 0 or page_number >= pdf_document.page_count:
            print(
                f"Page {page_number} does not exist in the document. The document has {pdf_document.page_count} pages.")
            return None

        page = pdf_document.load_page(page_number)
        page_text = page.get_text()
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


def find_cost_center(df):
    """Finds the cost center value in the DataFrame."""
    try:
        text = " ".join(df['line'].tolist())
        match = re.search(r'Centro de Custo\s*([\d]+)', text)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        print(f"Error finding cost center: {e}")
        return None


def extract_equipment_fields(file_path, page_number):
    """Extracts equipment fields from the PDF."""
    initial_data = "EQUIPAMENTO"
    final_data = "ORDEM DE MANUTENÇÃO"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    if no_data(df):
        return {}

    try:
        equipment_number = ""
        description_equipment = ""

        characteristics_index = df[df['line'].str.contains(
            "Características do Equipamento", case=False, na=False)].index

        if not characteristics_index.empty:
            next_lines = df.iloc[characteristics_index[0] +
                                 1:characteristics_index[0] + 3]['line'].str.strip().tolist()

            if len(next_lines) == 2 and next_lines[1].isdigit():
                equipment_number = next_lines[0]
                description_equipment = next_lines[1]
                df = df.drop(
                    df.index[characteristics_index[0] + 1:characteristics_index[0] + 3])
            else:
                df = df.drop(df.index[characteristics_index[0] + 1])

        extracted_fields = {
            "equipment_number": equipment_number,
            "description_equipment": description_equipment,
            "cost_center": find_value_after_label(df, "Centro de Custo", 11),
            "criticality": find_value_after_label(df, "Criticidade", 10),
            "installation_location": find_value_after_label(df, "Local de Instalação", 8),
            "description_installation_location": find_value_after_label(df, "Descrição do Local de Instalação", 8),
            "upper_installation_location": find_value_after_label(df, "Local de Instalação Superior", 6),
            "description_upper_installation_location": find_value_after_label(df, "Descrição do Local de Instalação Superior", 6),
        }

        return extracted_fields

    except Exception as e:
        print(f"Error extracting fields: {e}")
        return {}


def extract_maintenance_order_fields(file_path, page_number):
    """Extracts maintenance order fields from the PDF."""
    initial_data = "ORDEM DE MANUTENÇÃO"
    final_data = "NOTA DE MANUTENÇÃO"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    if no_data(df):
        return {}

    try:
        tipo_manutencao = find_value_after_label(df, "Tipo de Manutenção", 18)
        tipo_atividade = find_value_after_label(df, "Tipo de Atividade", 17)

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
            "operation_condition": find_value_after_label(df, "Condição de Operação", 11),
            "order_system_status": find_value_after_label(df, "Status Sistema Ordem", 2),
            "order_user_status": find_value_after_label(df, "Status Usuário Ordem", 2),
            "team": find_value_after_label(df, "Equipe", 11),
        }
        return extracted_fields

    except Exception as e:
        print(f"Error extracting fields: {e}")
        return {}


def extract_maintenance_note_fields(file_path, page_number):
    """Extracts maintenance note fields from the PDF."""
    initial_data = "NOTA DE MANUTENÇÃO"
    final_data = "DETALHAMENTO DA ORDEM"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    if no_data(df):
        return {}

    try:
        extracted_fields = {
            "note": find_value_after_label(df, "Nota", 6),
            "description": find_value_after_label(df, "Descrição", 5),
            "request_date": find_value_after_label(df, "Data Solicitação", 6),
            "author": find_value_after_label(df, "Autor", 6),
            "other_requests": find_value_after_label(df, "Outras Solicitações", 6),
        }
        return extracted_fields

    except Exception as e:
        print(f"Error extracting fields: {e}")
        return {}


def combine_fields(om, equipment_fields, order_fields, note_fields):
    """Combines equipment, maintenance order, and maintenance note fields into a single dictionary."""
    combined_data = {
        "om": om,
        "equipment_fields": equipment_fields,
        "order_fields": order_fields,
        "note_fields": note_fields
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
    input_pdf_path = './pdf/OM_00.pdf'
    marker = "PERMISSÃO DE TRABALHO SEGURO"
    output_dir = "./output_pdfs"

    separated_texts = process_pdf(input_pdf_path, output_dir, marker)
    all_combined_data = []

    for idx, (file_path, description_fields) in enumerate(separated_texts):
        try:
            om = description_fields.get("om", f"document_{idx + 1}")
            equipment_fields = extract_equipment_fields(file_path, 1)
            order_fields = extract_maintenance_order_fields(file_path, 1)
            note_fields = extract_maintenance_note_fields(file_path, 1)

            if om and equipment_fields and order_fields and note_fields:
                combined_data = combine_fields(
                    om, equipment_fields, order_fields, note_fields)
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
