'''
-----------------------------
Using the PdfWriter Class
-----------------------------
'''

from pathlib import Path

from pypdf import PdfReader, PdfWriter

# output_pdf = PdfWriter()
# page = output_pdf.add_blank_page(width=8.27 * 72, height=11.7 * 72)

# print(type(page))
# output_pdf.write('blank.pdf')

'''
-----------------------------
Extracting a Single Page From a PDF
-----------------------------
'''

# Change the path to work on your computer if necessary
# pdf_path = (
#     Path.cwd().parent
#     / "practice_files"
#     / "Pride_and_Prejudice.pdf"
# )

# input_pdf = PdfReader(pdf_path)
# first_page = input_pdf.pages[0]
# output_pdf = PdfWriter()
# output_pdf.add_page(first_page)
# output_pdf.write("first_page.pdf")


'''
-----------------------------
Extracting Multiple Pages From a PDF
-----------------------------
'''
