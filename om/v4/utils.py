import json
import os

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


def save_to_json(data, file_name):
    """Saves data to a JSON file."""
    try:
        with open(file_name, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {file_name}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")


def no_data(df):
    """Checks if the DataFrame is empty."""
    if df is None or df.empty:
        print("No data to extract.")
        return True
    return False
