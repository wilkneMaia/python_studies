import os

from PyPDF3 import PdfFileReader
from PyPDF3 import PdfFileWriter


def combine_pdfs(pdf_list, output_path):
    pdf_writer = PdfFileWriter()

    for pdf_path in pdf_list:
        pdf_reader = PdfFileReader(pdf_path)
        for page_num in range(pdf_reader.getNumPages()):
            page = pdf_reader.getPage(page_num)
            pdf_writer.addPage(page)

    with open(output_path, 'wb') as out_pdf_file:
        pdf_writer.write(out_pdf_file)

    print(f'Arquivos PDF combinados salvos em: {output_path}')


def get_pdf_list(input_folder):
    pdf_list = [os.path.join(input_folder, file) for file in os.listdir(
        input_folder) if file.endswith('.pdf')]
    pdf_list.sort()  # Ordena a lista de PDFs para garantir a ordem correta
    return pdf_list


def main():
    input_folder = './pdfs'  # Diretório contendo os arquivos PDF a serem combinados
    output_path = './combined_document.pdf'  # Caminho do arquivo PDF combinado

    pdf_list = get_pdf_list(input_folder)
    combine_pdfs(pdf_list, output_path)


if __name__ == '__main__':
    main()
