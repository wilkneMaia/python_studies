import json

import fitz  # PyMuPDF

import pandas as pd


def extract_maintenance_order_data(file_path, page_number, initial_data, final_data):
    """
    Extrai os dados de manutenção do PDF entre as seções initial_data e final_data.

    :param file_path: Caminho para o arquivo PDF
    :param page_number: Número da página a ser lida
    :param initial_data: Texto inicial para extração
    :param final_data: Texto final para extração
    :return: DataFrame com os dados extraídos ou None em caso de erro
    """
    try:
        # Abrir o arquivo PDF
        pdf_document = fitz.open(file_path)

        # Verificar se a página solicitada existe
        if page_number < 0 or page_number >= pdf_document.page_count:
            print(
                f"A página {page_number} não existe no documento. O documento tem {pdf_document.page_count} páginas.")
            return None

        # Obter a página
        page = pdf_document.load_page(page_number)

        # Extrair o texto da página
        page_text = page.get_text()

        # Localizar as seções initial_data e final_data
        order_start = page_text.find(initial_data)
        note_start = page_text.find(final_data)

        if order_start == -1 or note_start == -1:
            print(
                f"As seções {initial_data} e/ou {final_data} não foram encontradas na página.")
            return None

        # Extrair o texto entre as seções
        order_data = page_text[order_start:note_start].strip()

        # Dividir o texto em linhas para criar um DataFrame
        lines = order_data.split('\n')
        df = pd.DataFrame(lines, columns=['line'])

        return df

    except Exception as e:
        print(f"Erro ao abrir o arquivo: {e}")
        return None


def no_data(df):
    """
    Verifica se o DataFrame está vazio.

    :param df: DataFrame a ser verificado
    :return: True se o DataFrame estiver vazio ou None, False caso contrário
    """
    if df is None or df.empty:
        print("Nenhum dado para extrair.")
        return True
    return False


def save_to_json(data, file_name):
    """
    Salva os dados em um arquivo JSON.

    :param data: Dados a serem salvos
    :param file_name: Nome do arquivo JSON
    """
    try:
        with open(file_name, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Dados salvos com sucesso em {file_name}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo JSON: {e}")


def find_value_after_label(df, label, offset=1):
    """
    Encontra o valor no DataFrame após uma determinada etiqueta.

    :param df: DataFrame
    :param label: Etiqueta a ser encontrada
    :param offset: Número de linhas após a etiqueta para encontrar o valor
    :return: Valor encontrado ou None
    """
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


def extract_description(file_path, page_number):

    initial_data = "EQUIPAMENTO"
    final_data = "ORDEM DE MANUTENÇÃO"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    if no_data(df):
        return {}

    try:
        extracted_fields = {
            "N° OM:": find_value_after_label(df, "N° OM:", 5),
            "DESCRIÇÃO OM:": find_value_after_label(df, "DESCRIÇÃO OM:", 5),
        }

        return extracted_fields

    except Exception as e:
        print(f"Erro ao extrair os campos: {e}")
        return {}


def extract_equipment_fields(file_path, page_number):
    """
    Extrai os campos de equipamento do PDF.

    :param file_path: Caminho para o arquivo PDF
    :param page_number: Número da página a ser lida
    :return: Dicionário com os campos extraídos
    """
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
        # Exibir os campos extraídos
        print("Campos extraídos:")
        for key, value in extracted_fields.items():
            print(f"{key}: {value}")

        return extracted_fields

    except Exception as e:
        print(f"Erro ao extrair os campos: {e}")
        return {}


def extract_maintenance_order_fields(file_path, page_number):
    """
    Extrai os campos da ordem de manutenção do PDF.

    :param file_path: Caminho para o arquivo PDF
    :param page_number: Número da página a ser lida
    :return: Dicionário com os campos extraídos
    """
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
            # "responsible": find_value_after_label(df, "Responsável", 14),
            # "planner": find_value_after_label(df, "Planejador", 12),
        }

        # Exibir os campos extraídos
        print("Campos extraídos:")
        for key, value in extracted_fields.items():
            print(f"{key}: {value}")

        return extracted_fields

    except Exception as e:
        print(f"Erro ao extrair os campos: {e}")
        return {}


def extract_maintenance_note_fields(file_path, page_number):
    """
    Extrai os campos da nota de manutenção do PDF.

    :param file_path: Caminho para o arquivo PDF
    :param page_number: Número da página a ser lida
    :return: Dicionário com os campos extraídos
    """
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

        # Exibir os campos extraídos
        print("Campos extraídos:")
        for key, value in extracted_fields.items():
            print(f"{key}: {value}")

        return extracted_fields

    except Exception as e:
        print(f"Erro ao extrair os campos: {e}")
        return {}


def combine_fields(description_fields, equipment_fields, order_fields, note_fields):
    """
    Combina os campos de equipamento, ordem de manutenção e nota de manutenção em um único dicionário.

    :param equipment_fields: Campos de equipamento
    :param order_fields: Campos da ordem de manutenção
    :param note_fields: Campos da nota de manutenção
    :return: Dicionário combinado
    """
    combined_data = {
        "description": description_fields,
        "equipment": equipment_fields,
        "maintenance_order": order_fields,
        "maintenance_note": note_fields
    }
    return combined_data


# Exemplo de uso
if __name__ == "__main__":
    file_path = './pdf/OM_00.pdf'
    try:
        description_fields = extract_description(file_path, 0)
        equipment_fields = extract_equipment_fields(file_path, 1)
        order_fields = extract_maintenance_order_fields(file_path, 1)
        note_fields = extract_maintenance_note_fields(file_path, 1)

        if description_fields and equipment_fields and order_fields and note_fields:
            combined_data = combine_fields(
                description_fields, equipment_fields, order_fields, note_fields)
            save_to_json(combined_data, 'combined_maintenance_data.json')
        else:
            print("Não foi possível extrair dados suficientes para combinar.")
    except Exception as e:
        print(f"Erro durante o processamento: {e}")
