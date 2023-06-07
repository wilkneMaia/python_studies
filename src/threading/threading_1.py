import threading
import time
import webbrowser

# Este script cria uma thread separada para executar a função extrair_dados_site
# em paralelo com a função principal. A função extrair_dados_site abre um site
# especificado em uma nova janela do navegador e simula a extração de dados do
# site por 20 segundos. Enquanto isso, a função baixar_arquivos é executada na
# thread principal e simula o download de arquivos por 10 segundos.
# Quando ambas as funções são concluídas, o script informa que a extração de
# dados e o download dos arquivos foram concluídos.

def extrair_dados_site(site):
    # Abre o site especificado em uma nova janela do navegador
    print(f'estamos navegando até o site {site}')
    webbrowser.open_new(site)

    # Simula a extração de dados do site por 20 segundos
    for i in range(1, 20):
        print(f'Processando dados - {i}/19')
        time.sleep(1)

    # Informa que a extração de dados foi concluída
    print('Finalizado extração de dados do site!')

def baixar_arquivos():
    # Simula o download de arquivos por 10 segundos
    for i in range(1, 10):
        print(f'Baixado arquivos - {i}/9')
        time.sleep(1)

    # Informa que o download dos arquivos foi concluído
    print('Arquivos baixados')

# Cria uma nova thread para executar a função extrair_dados_site em paralelo com a função principal
nova_theading = threading.Thread(
    target=extrair_dados_site, args=('https://www.google.com',), daemon=True
)

nova_theading.start() # Inicia a execução da thread criada
baixar_arquivos() # Executa a função baixar_arquivos na thread principal
nova_theading.join() # Aguarda a conclusão da execução da thread criada antes de encerrar o programa

'''
    Se quiser execultar baixar_arquivos() somente quando a nova_theading for finalizada!

    $ nova_theading.start()
    $ nova_theading.join()
    $ baixar_arquivos()
'''
