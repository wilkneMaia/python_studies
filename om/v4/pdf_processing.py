import os
import fitz  # PyMuPDF

from helpers import extract_maintenance_order_data, find_value_after_label
from PyPDF3 import PdfFileReader
from utils import create_directory
from utils import save_pdf_range


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

            description_fields = extract_description_fields(output_pdf_path, 0)
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

        description_fields = extract_description_fields(output_pdf_path, 0)
        om = description_fields.get(
            "om", f"document_{start_page + 1}_to_{input_pdf_pypdf2.getNumPages()}")
        new_output_pdf_path = os.path.join(output_folder, f'{om}.pdf')
        os.rename(output_pdf_path, new_output_pdf_path)

        separated_texts.append((new_output_pdf_path, description_fields))

    return separated_texts


def extract_description_fields(file_path, page_number):
    """Extracts description fields from the PDF."""
    initial_data = "CENTRO EMITENTE:"
    final_data = "OBSERVAÇÕES:"
    df = extract_maintenance_order_data(
        file_path, page_number, initial_data, final_data)

    if df is None or df.empty:
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
