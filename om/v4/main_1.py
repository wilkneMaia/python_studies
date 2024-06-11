import json
import os
import re

import fitz  # PyMuPDF

from PyPDF3 import PdfFileReader
from PyPDF3 import PdfFileWriter
from utils import create_directory
from utils import no_data
from utils import save_pdf_range
from utils import save_to_excel
from utils import save_to_json

import pandas as pd


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


def extract_description(file_path, page_number):
    """Extracts description fields from the PDF."""
    initial_data = "CENTRO EMITENTE:"
    final_data = "OBSERVAÇÕES:"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)


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


def contains_om_number(text):
    # Define a expressão regular para corresponder 'OM' seguido por qualquer número
    pattern = r'OM \d+'
    # Use a função search do módulo re para procurar a expressão no texto
    match = re.search(pattern, text)
    # Retorne True se encontrar uma correspondência, caso contrário, False
    return bool(match)


def extract_description_fields(file_path, page_number):
    """Extracts description fields from the PDF."""
    initial_data = "CENTRO EMITENTE:"
    final_data = "OBSERVAÇÕES:"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    if df is None:
        return {}

    try:
        # Mapeamento de colunas para linhas
        columns_mapping = {
            "om": 1,
            "issue_center": 1,
            "center_plant": 1,
            "om_description": 1,
        }

        extracted_fields = {
            "om": find_value_after_label(df, "N° OM:", columns_mapping["om"]),
            "issue_center": find_value_after_label(df, "CENTRO EMITENTE:", columns_mapping["issue_center"]),
            "center_plant": find_value_after_label(df, "CENTRO/PLANTA:", columns_mapping["center_plant"]),
            "om_description": find_value_after_label(df, "DESCRIÇÃO OM:", columns_mapping["om_description"]),
        }
        return extracted_fields

    except Exception as e:
        print(f"Error extracting fields: {e}")
        return {}


def extract_equipment_fields(file_path, page_number):
    """
    Extracts equipment fields from the PDF.
    """
    initial_data = r'OM \d+'  # Regex to find initial data
    final_data = "ORDEM DE MANUTENÇÃO"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    # if no_data(df):
    #     return {}

    try:
        # Mapeamento de colunas para linhas
        columns_mapping = {
            "equipment_number": 12,
            "description_equipment": 1,
            "cost_center": 12,
            "criticality": 12,
            "installation_location": 11,
            "description_installation_location": 11,
            "upper_installation_location": 9,
            "description_upper_installation_location": 9,
            "equipment_characteristics": 9
        }

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
                cost_center = find_value_after_label(
                    df, "Centro de Custo", columns_mapping["cost_center"])
                criticality = find_value_after_label(
                    df, "Criticidade", columns_mapping["criticality"])
                installation_location = find_value_after_label(
                    df, "Local de Instalação", columns_mapping["installation_location"])
                description_installation_location = find_value_after_label(
                    df, "Descrição do Local de Instalação", columns_mapping["description_installation_location"])
                upper_installation_location = find_value_after_label(
                    df, "Local de Instalação Superior", columns_mapping["upper_installation_location"])
                description_upper_installation_location = find_value_after_label(
                    df, "Descrição do Local de Instalação Superior", columns_mapping["description_upper_installation_location"])

            elif contains_om_number(first_line):
                equipment_number = find_value_after_label(
                    df, "Número", columns_mapping["equipment_number"])
                description_equipment = find_value_after_label(
                    df, "Descrição Equipamento", columns_mapping["description_equipment"])
                cost_center = find_value_after_label(
                    df, "Centro de Custo", columns_mapping["cost_center"])
                criticality = find_value_after_label(
                    df, "Criticidade", columns_mapping["criticality"])
                installation_location = find_value_after_label(
                    df, "Local de Instalação", columns_mapping["installation_location"])
                description_installation_location = find_value_after_label(
                    df, "Descrição do Local de Instalação", columns_mapping["description_installation_location"])
                upper_installation_location = find_value_after_label(
                    df, "Local de Instalação Superior", columns_mapping["upper_installation_location"])
                description_upper_installation_location = find_value_after_label(
                    df, "Descrição do Local de Instalação Superior", columns_mapping["description_upper_installation_location"])
                equipment_characteristics = find_value_after_label(
                    df, "Características do Equipamento", columns_mapping["equipment_characteristics"])

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


def extract_maintenance_order_fields(file_path, page_number):
    """Extracts maintenance order fields from the PDF."""
    initial_data = "ORDEM DE MANUTENÇÃO"
    final_data = "NOTA DE MANUTENÇÃO"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    # if no_data(df):
    #     return {}

    try:
        # Mapeamento de colunas para linhas
        columns_mapping = {
            "Data Inicio": 21,
            "Hora Início": 20,
            "Data Fim": 19,
            "Hora Fim": 19,
            "Duração": 19,
            "Prioridade": 18,
            "Tipo de Manutenção": 18,
            "Tipo de Atividade": 18,
            "Ponto de Partida": 4,
            "Comprimento": 4,
            "Plano de Manutenção": 16,
            "Descrição do Plano": 16,
            "Condição de Operação": 14,
            "Status Sistema Ordem": 2,
            "Status Usuário Ordem": 2,
            "Equipe": 14,
        }

        line = df.iloc[34]['line'].strip()
        line_2 = df.iloc[35]['line'].strip()

        tipo_manutencao = find_value_after_label(
            df, "Tipo de Manutenção", columns_mapping["Tipo de Manutenção"])
        tipo_atividade = find_value_after_label(
            df, "Tipo de Atividade", columns_mapping["Tipo de Atividade"])

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
            tem = find_value_after_label(
                df, "Equipe", columns_mapping["Equipe"])
            plan_maintenance = find_value_after_label(
                df, "Plano de Manutenção", columns_mapping["Plano de Manutenção"])
            plan_description = find_value_after_label(
                df, "Descrição do Plano", columns_mapping["Descrição do Plano"])
            operation_condition = find_value_after_label(
                df, "Condição de Operação", columns_mapping["Condição de Operação"])
            print("Equipe: fim")

        if tipo_manutencao == "Manutenção Corretiva não Reparo":
            tipo_manutencao = "Manutenção Corretiva"
            tipo_atividade = "Reparo"

        extracted_fields = {
            "start_date": find_value_after_label(df, "Data Inicio", columns_mapping["Data Inicio"]),
            "start_time": find_value_after_label(df, "Hora", columns_mapping["Hora Início"]),
            "end_date": find_value_after_label(df, "Data Fim", columns_mapping["Data Fim"]),
            "end_time": find_value_after_label(df, "Hora Fim", columns_mapping["Hora Fim"]),
            "duration": find_value_after_label(df, "Duração", columns_mapping["Duração"]),
            "priority": find_value_after_label(df, "Prioridade", columns_mapping["Prioridade"]),
            "maintenance_type": tipo_manutencao,
            "activity_type": tipo_atividade,
            "starting_point": find_value_after_label(df, "Ponto de Partida", columns_mapping["Ponto de Partida"]),
            "length": find_value_after_label(df, "Comprimento", columns_mapping["Comprimento"]),
            "plan_maintenance": plan_maintenance,
            "plan_description": plan_description,
            "operation_condition": operation_condition,
            "order_system_status": find_value_after_label(df, "Status Sistema Ordem", columns_mapping["Status Sistema Ordem"]),
            "order_user_status": find_value_after_label(df, "Status Usuário Ordem", columns_mapping["Status Usuário Ordem"]),
            "team": tem,
        }
        return extracted_fields

    except Exception as e:
        print(f"Error extracting fields: {e}")
        return {}


if __name__ == "__main__":
    # Example of use
    file_path = '../v2/pdf/202305028822.pdf'  # Path to the uploaded file
    page_number = 1  # Page number you want to view
    # initial_data_regex = r'OM \d+'  # Regex to find initial data
    initial_data_regex = "ORDEM DE MANUTENÇÃO"
    final_data = "NOTA DE MANUTENÇÃO"

    # df = extract_maintenance_order_data(
    #     file_path, page_number, initial_data_regex, final_data)
    # print(df)

    extracted_description_fields = extract_description_fields(file_path, 0)
    print(json.dumps(extracted_description_fields, indent=4))

    extracted_equipment_fields = extract_equipment_fields(
        file_path, 1)
    print(json.dumps(extracted_equipment_fields, indent=4))

    extracted_fields = extract_maintenance_order_fields(file_path, 1)
    print(json.dumps(extracted_fields, indent=4))
