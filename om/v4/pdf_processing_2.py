# import os
# import re

# import fitz  # PyMuPDF

# from PyPDF3 import PdfFileReader
# from PyPDF3 import PdfFileWriter
# from utils import create_directory
# from utils import save_pdf_range

# import pandas as pd


# def extract_maintenance_order_data(file_path, page_number, initial_data_regex, final_data):
#     """Extracts maintenance order data from the PDF between initial_data_regex and final_data sections."""
#     try:
#         pdf_document = fitz.open(file_path)

#         if page_number < 0 or page_number >= pdf_document.page_count:
#             print(
#                 f"Page {page_number} does not exist in the document. The document has {pdf_document.page_count} pages.")
#             return None

#         page = pdf_document.load_page(page_number)
#         page_text = page.get_text()

#         # Use regex to find the initial data matching the provided regex
#         initial_data_match = re.search(initial_data_regex, page_text)
#         if not initial_data_match:
#             print(
#                 f"Initial data matching regex '{initial_data_regex}' not found.")
#             return None

#         initial_data = initial_data_match.group()
#         order_start = page_text.find(initial_data)
#         note_start = page_text.find(final_data)

#         if order_start == -1 or note_start == -1:
#             print(
#                 f"Sections {initial_data} and/or {final_data} were not found on the page.")
#             return None

#         order_data = page_text[order_start:note_start].strip()
#         lines = order_data.split('\n')
#         df = pd.DataFrame(lines, columns=['line'])

#         return df

#     except Exception as e:
#         print(f"Error opening file: {e}")
#         return None


# def process_pdf(input_pdf_path, output_folder, marker, extract_description_fields):
#     """Processes the PDF to split documents based on the marker."""
#     create_directory(output_folder)
#     input_pdf_fitz = fitz.open(input_pdf_path)
#     input_pdf_pypdf2 = PdfFileReader(input_pdf_path)

#     current_page = 0
#     start_page = 0
#     separated_texts = []
#     pdf_writer = PdfFileWriter()

#     while current_page < input_pdf_pypdf2.getNumPages():
#         page = input_pdf_fitz.load_page(current_page)
#         text = page.get_text("text")
#         normalized_text = " ".join(text.split())

#         if marker in normalized_text and current_page != 0:
#             end_page = current_page - 1
#             output_pdf_path = os.path.join(
#                 output_folder, f'document_{start_page + 1}_to_{end_page + 1}.pdf'
#             )
#             save_pdf_range(input_pdf_pypdf2, start_page,
#                            end_page, output_pdf_path, pdf_writer)

#             description_fields = extract_description_fields(output_pdf_path, 0)
#             om = description_fields.get(
#                 "om", f"document_{start_page + 1}_to_{end_page + 1}")
#             new_output_pdf_path = os.path.join(output_folder, f'{om}.pdf')
#             os.rename(output_pdf_path, new_output_pdf_path)

#             print(f"Created PDF: {new_output_pdf_path}")
#             print(f"Description Fields: {description_fields}")

#             separated_texts.append((new_output_pdf_path, description_fields))

#             start_page = current_page

#         current_page += 1

#     if start_page < input_pdf_pypdf2.getNumPages():
#         output_pdf_path = os.path.join(
#             output_folder, f'document_{start_page + 1}_to_{input_pdf_pypdf2.getNumPages()}.pdf'
#         )
#         save_pdf_range(input_pdf_pypdf2, start_page, input_pdf_pypdf2.getNumPages(
#         ) - 1, output_pdf_path, pdf_writer)

#         description_fields = extract_description_fields(output_pdf_path, 0)
#         om = description_fields.get(
#             "om", f"document_{start_page + 1}_to_{input_pdf_pypdf2.getNumPages()}")
#         new_output_pdf_path = os.path.join(output_folder, f'{om}.pdf')
#         os.rename(output_pdf_path, new_output_pdf_path)

#         print(f"Created PDF: {new_output_pdf_path}")
#         print(f"Description Fields: {description_fields}")

#         separated_texts.append((new_output_pdf_path, description_fields))

#     return separated_texts
