import fitz  # PyMuPDF


# Define the input path
input_pdf_path = 'SEMANA_01.pdf'

# Read the input PDF with PyMuPDF to extract text
input_pdf = fitz.open(input_pdf_path)

# Extract text from each page
text_data = []
for page_num in range(input_pdf.page_count):
    page = input_pdf.load_page(page_num)
    text = page.get_text("text")
    text_data.append(text)

# Save the extracted text to a file (optional)
with open('extracted_text.txt', 'w') as file:
    file.write('\n'.join(text_data))

print("Text extraction completed.")
