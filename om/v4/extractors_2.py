import re

from om.v4.pdf_processing_2 import extract_maintenance_order_data
from utils import no_data


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


# def verificar_texto_in(texto_maior, texto_especifico):
#     return texto_especifico in texto_maior


def contains_om_number(text):
    """Check if text contains 'OM' followed by any number."""
    pattern = r'OM \d+'
    return bool(re.search(pattern, text))


def extract_description_fields(file_path, page_number):
    """Extracts description fields from the PDF."""
    initial_data = "CENTRO EMITENTE:"
    final_data = "OBSERVAÇÕES:"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    if df is None:
        return {}

    try:
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
    """Extracts equipment fields from the PDF."""
    initial_data = r'OM \d+'  # Regex to find initial data
    final_data = "ORDEM DE MANUTENÇÃO"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    if no_data(df):
        return {}

    try:
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

        first_line = df.iloc[0]['line'].strip()
        third_line = df.iloc[2]['line'].strip()

        if third_line == "EQUIPAMENTO":
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

    if df is None:
        return {}

    try:
        columns_mapping = {
            "start_date": 21,
            "start_time": 20,
            "end_date": 19,
            "end_time": 19,
            "duration": 19,
            "priority": 18,
            "maintenance_type": 18,
            "activity_type": 18,
            "starting_point": 4,
            "length": 4,
            "plan_maintenance": 16,
            "plan_description": 16,
            "operation_condition": 14,
            "order_system_status": 2,
            "order_user_status": 2,
            "team": 14
        }

        line = df.iloc[34]['line'].strip()
        line_2 = df.iloc[35]['line'].strip()

        tipo_manutencao = find_value_after_label(
            df, "Tipo de Manutenção", columns_mapping["maintenance_type"])
        tipo_atividade = find_value_after_label(
            df, "Tipo de Atividade", columns_mapping["activity_type"])

        if line == "Status Sistema Ordem":
            tem = find_value_after_label(df, "Equipe", 11)
            plan_maintenance = ""
            plan_description = ""
            operation_condition = find_value_after_label(
                df, "Condição de Operação", 12)
        elif line_2 == "Status Sistema Ordem":
            tem = find_value_after_label(df, "Equipe", 12)
            plan_maintenance = ""
            plan_description = ""
            operation_condition = find_value_after_label(
                df, "Condição de Operação", 12)
        else:
            tem = find_value_after_label(df, "Equipe", columns_mapping["team"])
            plan_maintenance = find_value_after_label(
                df, "Plano de Manutenção", columns_mapping["plan_maintenance"])
            plan_description = find_value_after_label(
                df, "Descrição do Plano", columns_mapping["plan_description"])
            operation_condition = find_value_after_label(
                df, "Condição de Operação", columns_mapping["operation_condition"])

        if tipo_manutencao == "Manutenção Corretiva não Reparo":
            tipo_manutencao = "Manutenção Corretiva"
            tipo_atividade = "Reparo"

        extracted_fields = {
            "start_date": find_value_after_label(df, "Data Inicio", columns_mapping["start_date"]),
            "start_time": find_value_after_label(df, "Hora", columns_mapping["start_time"]),
            "end_date": find_value_after_label(df, "Data Fim", columns_mapping["end_date"]),
            "end_time": find_value_after_label(df, "Hora Fim", columns_mapping["end_time"]),
            "duration": find_value_after_label(df, "Duração", columns_mapping["duration"]),
            "priority": find_value_after_label(df, "Prioridade", columns_mapping["priority"]),
            "maintenance_type": tipo_manutencao,
            "activity_type": tipo_atividade,
            "starting_point": find_value_after_label(df, "Ponto de Partida", columns_mapping["starting_point"]),
            "length": find_value_after_label(df, "Comprimento", columns_mapping["length"]),
            "plan_maintenance": plan_maintenance,
            "plan_description": plan_description,
            "operation_condition": operation_condition,
            "order_system_status": find_value_after_label(df, "Status Sistema Ordem", columns_mapping["order_system_status"]),
            "order_user_status": find_value_after_label(df, "Status Usuário Ordem", columns_mapping["order_user_status"]),
            "team": tem,
        }
        return extracted_fields

    except Exception as e:
        print(f"Error extracting fields: {e}")
        return {}
