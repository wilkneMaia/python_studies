import json

import pytesseract

from pdf2image import convert_from_path


# Defina o caminho do arquivo PDF de entrada
input_pdf_path = '01.pdf'

# Converta as páginas do PDF em imagens
pages = convert_from_path(input_pdf_path)

# Defina a área a ser recortada (left, top, right, bottom)
# Estes valores são aproximados e devem ser ajustados conforme necessário
crop_area = (50, 50, 800, 400)  # Ajuste estes valores conforme necessário

# Inicialize uma lista vazia para armazenar os dados extraídos
data_list = []

# Processe cada página
for page_num, page in enumerate(pages):
    # Recorte a área especificada
    cropped_image = page.crop(crop_area)

    # Realize a OCR na imagem recortada
    text = pytesseract.image_to_string(cropped_image, lang='por')

    # Divida o texto em linhas e mapeie para chaves
    lines = text.split('\n')
    data = {
        "Número": "",
        "Descrição Equipamento": "",
        "Centro de Custo": "",
        "Criticidade": "",
        "Tipo Contador": "",
        "Nº Identificação Técnica": "",
        "Término da Garantia": "",
        "Fonte radioativa": "",
        "Local de Instalação": "",
        "Descrição do Local de Instalação": "",
        "Local de Instalação Superior": "",
        "Descrição do Local de Instalação Superior": "",
        "Características do Equipamento": ""
    }

    # Preencha o dicionário com os valores extraídos
    for line in lines:
        if "Número" in line:
            data["Número"] = line.split(":")[-1].strip()
        elif "Descrição Equipamento" in line:
            data["Descrição Equipamento"] = line.split(":")[-1].strip()
        elif "Centro de Custo" in line:
            data["Centro de Custo"] = line.split(":")[-1].strip()
        elif "Criticidade" in line:
            data["Criticidade"] = line.split(":")[-1].strip()
        elif "Tipo Contador" in line:
            data["Tipo Contador"] = line.split(":")[-1].strip()
        elif "Nº Identificação Técnica" in line:
            data["Nº Identificação Técnica"] = line.split(":")[-1].strip()
        elif "Término da Garantia" in line:
            data["Término da Garantia"] = line.split(":")[-1].strip()
        elif "Fonte radioativa" in line:
            data["Fonte radioativa"] = line.split(":")[-1].strip()
        elif "Local de Instalação" in line:
            data["Local de Instalação"] = line.split(":")[-1].strip()
        elif "Descrição do Local de Instalação" in line:
            data["Descrição do Local de Instalação"] = line.split(
                ":")[-1].strip()
        elif "Local de Instalação Superior" in line:
            data["Local de Instalação Superior"] = line.split(":")[-1].strip()
        elif "Descrição do Local de Instalação Superior" in line:
            data["Descrição do Local de Instalação Superior"] = line.split(
                ":")[-1].strip()
        elif "Características do Equipamento" in line:
            data["Características do Equipamento"] = line.split(
                ":")[-1].strip()

    # Adicione os dados extraídos à lista
    data_list.append(data)

# Salve os dados extraídos em um arquivo JSON
output_json_path = 'extracted_data.json'
with open(output_json_path, 'w', encoding='utf-8') as json_file:
    json.dump(data_list, json_file, ensure_ascii=False, indent=4)

print(f"Data extraction completed and saved to {output_json_path}.")
