import json
import os
import re

import fitz  # PyMuPDF

from PyPDF3 import PdfFileReader
from PyPDF3 import PdfFileWriter

import pandas as pd


def create_directory(directory):
    """
    Creates a directory if it doesn't exist.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_pdf_range(input_pdf, start_page, end_page, output_pdf_path):
    """
    Saves a range of pages as a separate PDF.
    """
    pdf_writer = PdfFileWriter()
    for page in range(start_page, end_page + 1):
        pdf_writer.addPage(input_pdf.getPage(page))
    with open(output_pdf_path, 'wb') as output_pdf_file:
        pdf_writer.write(output_pdf_file)
    print(f"Saved PDF: {output_pdf_path}")


def process_pdf(input_pdf_path, output_folder, marker):
    """
    Processes the PDF to split documents based on the marker.
    """
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
        print(
            f"Processing page {current_page}, normalized text: {normalized_text}")

        if marker in normalized_text and current_page != 0:
            end_page = current_page - 1

            # Extract information from the section
            section_text = ""
            for page_num in range(start_page, end_page + 1):
                section_text += input_pdf_fitz.load_page(
                    page_num).get_text("text")

            description_fields = extract_description(section_text)
            om_description = description_fields.get(
                "om", f"document_{start_page + 1}_to_{end_page + 1}")

            output_pdf_path = os.path.join(
                output_folder, f'{om_description}.pdf')
            save_pdf_range(input_pdf_pypdf2, start_page,
                           end_page, output_pdf_path)

            separated_texts.append(
                (output_pdf_path, description_fields, start_page, end_page))

            start_page = current_page

        current_page += 1

    if start_page < input_pdf_pypdf2.getNumPages():
        # Extract information from the last section
        section_text = ""
        for page_num in range(start_page, input_pdf_pypdf2.getNumPages()):
            section_text += input_pdf_fitz.load_page(page_num).get_text("text")

        description_fields = extract_description(section_text)
        om_description = description_fields.get(
            "om", f"document_{start_page + 1}_to_{input_pdf_pypdf2.getNumPages()}")

        output_pdf_path = os.path.join(output_folder, f'{om_description}.pdf')
        save_pdf_range(input_pdf_pypdf2, start_page,
                       input_pdf_pypdf2.getNumPages() - 1, output_pdf_path)

        separated_texts.append(
            (output_pdf_path, description_fields, start_page, input_pdf_pypdf2.getNumPages() - 1))

    return separated_texts


def extract_description(text):
    """
    Extracts the description fields from the text.
    """
    extracted_fields = {}
    om_match = re.search(r'N° OM:\s*(\S+)', text)
    if om_match:
        extracted_fields['om'] = om_match.group(1)
    return extracted_fields


def extract_maintenance_order_data(file_path, page_number, initial_data, final_data):
    """
    Extrai os dados de manutenção do PDF entre as seções initial_data e final_data.
    """
    try:
        pdf_document = fitz.open(file_path)
        if page_number < 0 or page_number >= pdf_document.page_count:
            print(
                f"A página {page_number} não existe no documento. O documento tem {pdf_document.page_count} páginas.")
            return None
        page = pdf_document.load_page(page_number)
        page_text = page.get_text()
        order_start = page_text.find(initial_data)
        note_start = page_text.find(final_data)
        if order_start == -1 or note_start == -1:
            print(
                f"As seções {initial_data} e/ou {final_data} não foram encontradas na página.")
            return None
        order_data = page_text[order_start:note_start].strip()
        lines = order_data.split('\n')
        df = pd.DataFrame(lines, columns=['line'])
        return df
    except Exception as e:
        print(f"Erro ao abrir o arquivo: {e}")
        return None


def no_data(df):
    if df is None or df.empty:
        print("Nenhum dado para extrair.")
        return True
    return False


def save_to_json(data, file_name):
    try:
        with open(file_name, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Dados salvos com sucesso em {file_name}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo JSON: {e}")


def find_value_after_label(df, label, offset=1):
    try:
        index = df[df['line'].str.contains(label, case=False, na=False)].index
        if not index.empty:
            value_index = index[0] + offset
            if value_index < len(df):
                value = df.iloc[value_index]['line'].strip()
                return value
        return None
    except Exception as e:
        print(f"Erro ao encontrar valor após a etiqueta {label}: {e}")
        return None


def extract_equipment_fields(file_path, page_number):
    initial_data = "EQUIPAMENTO"
    final_data = "ORDEM DE MANUTENÇÃO"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)
    if no_data(df):
        return {}
    try:
        extracted_fields = {
            "cost_center": find_value_after_label(df, "Centro de Custo", 11),
            "criticality": find_value_after_label(df, "Criticidade", 11),
            "installation_location": find_value_after_label(df, "Local de Instalação", 9),
            "description_installation_location": find_value_after_label(df, "Descrição do Local de Instalação", 9),
            "upper_installation_location": find_value_after_label(df, "Local de Instalação Superior", 7),
            "description_upper_installation_location": find_value_after_label(df, "Descrição do Local de Instalação Superior", 7),
        }
        print("Campos extraídos:")
        for key, value in extracted_fields.items():
            print(f"{key}: {value}")
        return extracted_fields
    except Exception as e:
        print(f"Erro ao extrair os campos: {e}")
        return {}


def extract_maintenance_order_fields(file_path, page_number):
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
        print("Campos extraídos:")
        for key, value in extracted_fields.items():
            print(f"{key}: {value}")
        return extracted_fields
    except Exception as e:
        print(f"Erro ao extrair os campos: {e}")
        return {}


def extract_maintenance_note_fields(file_path, page_number):
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
        print("Campos extraídos:")
        for key, value in extracted_fields.items():
            print(f"{key}: {value}")
        return extracted_fields
    except Exception as e:
        print(f"Erro ao extrair os campos: {e}")
        return {}


def combine_fields(om, equipment_fields, order_fields, note_fields):
    """
    Combina os campos de equipamento, ordem de manutenção e nota de manutenção em um único dicionário.

    :param om: Número OM
    :param equipment_fields: Campos de equipamento
    :param order_fields: Campos da ordem de manutenção
    :param note_fields: Campos da nota de manutenção
    :return: Dicionário combinado
    """
    combined_data = {
        "om": om,
        "equipment": equipment_fields,
        "maintenance_order": order_fields,
        "maintenance_note": note_fields
    }
    return combined_data


def main():
    input_pdf_path = './pdf/OM_00.pdf'
    marker = "PERMISSÃO DE TRABALHO SEGURO"
    output_dir = "./output_pdfs"

    separated_texts = process_pdf(input_pdf_path, output_dir, marker)
    all_combined_data = []

    for idx, (file_path, description_fields, _, _) in enumerate(separated_texts):
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
                    f"Não foi possível extrair dados suficientes para combinar para o documento {idx + 1}.")
        except Exception as e:
            print(f"Erro durante o processamento do documento {idx + 1}: {e}")

    json_file_path = f"{output_dir}/combined_maintenance_data.json"
    save_to_json(all_combined_data, json_file_path)


if __name__ == "__main__":
    main()
