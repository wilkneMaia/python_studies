# import json

# import fitz  # PyMuPDF

# import pandas as pd


# def extract_maintenance_order_data(file_path, page_number):
#     try:
#         # Abrir o arquivo PDF
#         pdf_document = fitz.open(file_path)

#         # Verificar se a página solicitada existe
#         if page_number < 0 or page_number >= pdf_document.page_count:
#             print(
#                 f"A página {page_number} não existe no documento. O documento tem {pdf_document.page_count} páginas.")
#             return None

#         # Obter a página
#         page = pdf_document.load_page(page_number)

#         # Extrair o texto da página
#         page_text = page.get_text("text")

#         # Dividir o texto em linhas
#         lines = page_text.splitlines()

#         # Organizar em DataFrame do pandas
#         df = pd.DataFrame(lines, columns=["line"])

#         # Imprimir todas as linhas do DataFrame para localizar os dados
#         print("Linhas extraídas do PDF:")
#         for index, row in df.iterrows():
#             print(f"{index}: {row['line']}")

#         return df

#     except Exception as e:
#         print(f"Erro ao abrir o arquivo: {e}")
#         return None


# def find_value_after_label(df, label, offset=1):
#     index = df[df['line'].str.contains(label, case=False, na=False)].index
#     if not index.empty:
#         value_index = index[0] + offset
#         if value_index < len(df):
#             value = df.iloc[value_index]['line'].strip()
#             return value
#     return None


# def extract_fields(df):
#     if df is None or df.empty:
#         print("Nenhum dado para extrair.")
#         return {}

#     # Ajustar os offsets corretamente com base nas linhas extraídas
#     extracted_fields = {
#         "Data Inicio": find_value_after_label(df, "Data Inicio", 21),
#         "Hora Início": find_value_after_label(df, "Hora", 20),
#         "Data Fim": find_value_after_label(df, "Data Fim", 19),
#         "Hora Fim": find_value_after_label(df, "Hora", 22),
#     }

#     return extracted_fields


# def save_to_json(data, file_name):
#     with open(file_name, 'w', encoding='utf-8') as json_file:
#         json.dump(data, json_file, ensure_ascii=False, indent=4)


# # Exemplo de uso
# if __name__ == "__main__":
#     file_path = './pdf/OM_00.pdf'
#     page_number = 1  # Número da página que você quer visualizar
#     df = extract_maintenance_order_data(file_path, page_number)

#     if df is not None:
#         extracted_fields = extract_fields(df)
#         print("Campos extraídos:")
#         for key, value in extracted_fields.items():
#             print(f"{key}: {value}")

#         # Criar a estrutura de dados para o JSON
#         data_json = {
#             "om": {
#                 "data_inicial": extracted_fields.get("Data Inicio"),
#                 "hora_inicial": extracted_fields.get("Hora Início"),
#                 "data_final": extracted_fields.get("Data Fim"),
#                 "hora_final": extracted_fields.get("Hora Fim"),
#                 # Adicione outros campos conforme necessário
#             }
#         }

#         # Salvar em um arquivo JSON
#         save_to_json([data_json], 'dados_extracao.json')
#         print("Dados salvos em 'dados_extracao.json'.")


# import json

# import fitz  # PyMuPDF

# import pandas as pd


# def extract_maintenance_order_data(file_path, page_number):
#     try:
#         # Abrir o arquivo PDF
#         pdf_document = fitz.open(file_path)

#         # Verificar se a página solicitada existe
#         if page_number < 0 or page_number >= pdf_document.page_count:
#             print(
#                 f"A página {page_number} não existe no documento. O documento tem {pdf_document.page_count} páginas.")
#             return None

#         # Obter a página
#         page = pdf_document.load_page(page_number)

#         # Extrair o texto da página
#         page_text = page.get_text("text")

#         # Dividir o texto em linhas
#         lines = page_text.splitlines()

#         # Organizar em DataFrame do pandas
#         df = pd.DataFrame(lines, columns=["line"])

#         # Imprimir todas as linhas do DataFrame para localizar os dados
#         print("Linhas extraídas do PDF:")
#         for index, row in df.iterrows():
#             print(f"{index}: {row['line']}")

#         return df

#     except Exception as e:
#         print(f"Erro ao abrir o arquivo: {e}")
#         return None


# def find_value_after_label(df, label, offset=1):
#     index = df[df['line'].str.contains(label, case=False, na=False)].index
#     if not index.empty:
#         value_index = index[0] + offset
#         if value_index < len(df):
#             value = df.iloc[value_index]['line'].strip()
#             # Certifique-se de que a linha seguinte não seja outro rótulo
#             if not any(keyword in value.lower() for keyword in ['data', 'hora', 'duração', 'prioridade']):
#                 return value
#     return None


# def extract_fields(df):
#     if df is None or df.empty:
#         print("Nenhum dado para extrair.")
#         return {}

#     # Extrair os valores com base em seus locais no DataFrame
#     extracted_fields = {
#         "Data Inicio": find_value_after_label(df, "Data Inicio"),
#         "Hora Início": find_value_after_label(df, "Hora Início"),
#         "Data Fim": find_value_after_label(df, "Data Fim"),
#         "Hora Fim": find_value_after_label(df, "Hora Fim"),
#     }

#     return extracted_fields


# def save_to_json(data, file_name):
#     with open(file_name, 'w', encoding='utf-8') as json_file:
#         json.dump(data, json_file, ensure_ascii=False, indent=4)


# # Exemplo de uso
# if __name__ == "__main__":
#     file_path = './pdf/OM_00.pdf'
#     page_number = 1  # Número da página que você quer visualizar
#     df = extract_maintenance_order_data(file_path, page_number)

#     if df is not None:
#         extracted_fields = extract_fields(df)
#         print("Campos extraídos:")
#         for key, value in extracted_fields.items():
#             print(f"{key}: {value}")

#         # Criar a estrutura de dados para o JSON
#         data_json = {
#             "om": {
#                 "data_inicial": extracted_fields.get("Data Inicio"),
#                 "hora_inicial": extracted_fields.get("Hora Início"),
#                 "data_final": extracted_fields.get("Data Fim"),
#                 "hora_final": extracted_fields.get("Hora Fim"),
#                 # Adicione outros campos conforme necessário
#             }
#         }

#         # Salvar em um arquivo JSON
#         save_to_json([data_json], 'dados_extracao.json')
#         print("Dados salvos em 'dados_extracao.json'.")


import re

import fitz  # PyMuPDF


def extract_maintenance_order_data(file_path, page_number):
    try:
        # Abrir o arquivo PDF
        pdf_document = fitz.open(file_path)

        # Verificar se a página solicitada existe
        if page_number < 0 or page_number >= pdf_document.page_count:
            print(
                f"A página {page_number} não existe no documento. O documento tem {pdf_document.page_count} páginas.")
            return

        # Obter a página
        page = pdf_document.load_page(page_number)

        # Extrair o texto da página
        page_text = page.get_text()

        # Localizar as seções "ORDEM DE MANUTENÇÃO" e "NOTA DE MANUTENÇÃO"
        order_start = page_text.find("N° OM:")
        note_start = page_text.find("OBSERVAÇÕES:")

        if order_start == -1 or note_start == -1:
            print(
                "As seções 'ORDEM DE MANUTENÇÃO' e/ou 'NOTA DE MANUTENÇÃO' não foram encontradas na página.")
            return

        # Extrair o texto entre as seções
        order_data = page_text[order_start:note_start].strip()

        # Exibir o texto extraído
        print(f"Dados da 'ORDEM DE MANUTENÇÃO':\n{order_data}")
        return order_data

    except Exception as e:
        print(f"Erro ao abrir o arquivo: {e}")


# # Exemplo de uso
file_path = './pdf/OM_00.pdf'
page_number = 0  # Número da página que você quer visualizar
order_data = extract_maintenance_order_data(file_path, page_number)


# def extract_fields(order_data):
#     fields = {
#         "Data Inicio": re.search(r"Data Inicio\s*([0-9]{2}/[0-9]{2}/[0-9]{4})", order_data),
#         "Hora Início": re.search(r"Hora\s*Início\s*([0-9]{2}:[0-9]{2})", order_data),
#         # "Data Fim": re.search(r"Data Fim\s*([0-9]{2}/[0-9]{2}/[0-9]{4})", order_data),
#         # "Hora Fim": re.search(r"Hora Fim\s*([0-9]{2}:[0-9]{2})", order_data),
#         # "Duração (h)": re.search(r"Duração\s*\(h\)\s*([0-9]+\.[0-9]+)", order_data),
#         # "Prioridade": re.search(r"Prioridade\s*(\w+)", order_data),
#         # "Tipo de Manutenção": re.search(r"Tipo de Manutenção\s*([\w\s]+)", order_data),
#         # "Ponto de Partida": re.search(r"Ponto de Partida\s*([\w\s-]+)", order_data),
#         # "Plano de Manutenção": re.search(r"Plano de Manutenção\s*([\w\s-]+)", order_data),
#     }

#     # Extrair os valores correspondentes das expressões regulares
#     extracted_fields = {key: (match.group(1) if match else None)
#                         for key, match in fields.items()}

#     return extracted_fields


# # Exemplo de uso
# if __name__ == "__main__":
#     extracted_fields = extract_fields(order_data)
#     print("Campos extraídos:")
#     for key, value in extracted_fields.items():
#         print(f"{key}: {value}")

# # if order_data:
# #     extracted_fields = extract_fields(order_data)
# #     for field, value in extracted_fields.items():
# #         print(f"{field}: {value}")

# # # Exemplo de uso
# # if __name__ == "__main__":
# #     file_path = './pdf/OM_00.pdf'
# #     page_number = 1  # Número da página que você quer visualizar
# #     extract_maintenance_order_data(file_path, page_number)
