import fitz  # PyMuPDF


def show_pdf_content(file_path, page_number):
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
        print(f"Conteúdo da página {page_number}:\n")
        print(page_text)

    except Exception as e:
        print(f"Erro ao abrir o arquivo: {e}")


if __name__ == "__main__":
    # Exemplo de uso
    file_path = './pdf/OM_00.pdf'
    page_number = 1  # Número da página que você quer visualizar
    show_pdf_content(file_path, page_number)


# def show_pdf_content(file_path):
#     try:
#         # Abrir o arquivo PDF
#         pdf_document = fitz.open(file_path)

#         # Exibir a quantidade de páginas
#         print(f"O documento tem {pdf_document.page_count} páginas.\n")

#         # Listar todas as páginas
#         for page_number in range(pdf_document.page_count):
#             print(f"Pág. {page_number+1}")
#             page = pdf_document.load_page(page_number)
#             page_text = page.get_text()
#             print(page_text[:200])  # Mostrar apenas os primeiros 200 caracteres para visualização
#             print("\n" + "-"*50 + "\n")

#         # Pedir ao usuário para selecionar uma página
#         selected_page = int(input("Digite o número da página que você deseja visualizar: ")) - 1

#         if selected_page < 0 or selected_page >= pdf_document.page_count:
#             print(f"A página {selected_page+1} não existe.")
#             return

#         # Mostrar o conteúdo da página selecionada
#         page = pdf_document.load_page(selected_page)
#         page_text = page.get_text()
#         print(f"\nConteúdo da página {selected_page+1}:\n")
#         print(page_text)

#     except Exception as e:
#         print(f"Erro ao abrir o arquivo: {e}")

# # Exemplo de uso
# file_path = 'caminho/para/seu/documento.pdf'
# show_pdf_content(file_path)


# # Exemplo de uso
# file_path = './pdf/OM_00.pdf'
# page_number = 0  # Número da página que você quer visualizar
# show_pdf_content(file_path, page_number)
