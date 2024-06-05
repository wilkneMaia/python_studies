import json
import os
import re

import pytesseract

from pdf2image import convert_from_path
from PIL import Image


# Configurar o caminho do Tesseract
# Ajuste este caminho conforme necessário
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

# Caminhos de entrada e saída
input_pdf_path = 'Ordens sistemáticas da BRITAGEM até 07.03.pdf'
output_json_path = 'output_data.json'

# Converter PDF para imagens
try:
    pages = convert_from_path(input_pdf_path, 300)
except Exception as e:
    print(f"Erro ao converter PDF para imagens: {e}")
    raise

# Função para extrair e limpar o texto usando OCR


def ocr_image(image):
    try:
        text = pytesseract.image_to_string(image, lang='por')
    except Exception as e:
        print(f"Erro ao executar OCR: {e}")
        text = ""
    return text

# Função para extrair informações com regex


def extract_info(text):
    info = {}

    def extract_field(field_name, pattern):
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ''

    info['Número'] = extract_field('Número', r'Número\s*([^\n]+)')
    info['Descrição Equipamento'] = extract_field(
        'Descrição Equipamento', r'Descrição Equipamento\s*([^\n]+)')
    info['Centro de Custo'] = extract_field(
        'Centro de Custo', r'Centro de Custo\s*([^\n]+)')
    info['Criticidade'] = extract_field(
        'Criticidade', r'Criticidade\s*([^\n]+)')
    info['Tipo Contador'] = extract_field(
        'Tipo Contador', r'Tipo Contador\s*([^\n]+)')
    info['Nº Identificação Técnica'] = extract_field(
        'Nº Identificação Técnica', r'Nº Identificação Técnica\s*([^\n]+)')
    info['Término da Garantia'] = extract_field(
        'Término da Garantia', r'Término da Garantia\s*([^\n]+)')
    info['Fonte radioativa'] = extract_field(
        'Fonte radioativa', r'Fonte radioativa\s*([^\n]+)')
    info['Local de Instalação'] = extract_field(
        'Local de Instalação', r'Local de Instalação\s*([^\n]+)')
    info['Descrição do Local de Instalação'] = extract_field(
        'Descrição do Local de Instalação', r'Descrição do Local de Instalação\s*([^\n]+)')
    info['Local de Instalação Superior'] = extract_field(
        'Local de Instalação Superior', r'Local de Instalação Superior\s*([^\n]+)')
    info['Descrição do Local de Instalação Superior'] = extract_field(
        'Descrição do Local de Instalação Superior', r'Descrição do Local de Instalação Superior\s*([^\n]+)')
    info['Características do Equipamento'] = extract_field(
        'Características do Equipamento', r'Características do Equipamento\s*([^\n]+)')

    return info


# Inicializa a lista para coletar as informações extraídas
info_list = []

# Processa cada página
for page in pages:
    text = ocr_image(page)
    if text:  # Verifica se o OCR retornou algum texto
        info = extract_info(text)
        info_list.append(info)

# Salva os dados extraídos em um arquivo JSON
try:
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(info_list, json_file, ensure_ascii=False, indent=4)
    print(f'Dados extraídos salvos em: {output_json_path}')
except Exception as e:
    print(f"Erro ao salvar os dados em JSON: {e}")
    raise
