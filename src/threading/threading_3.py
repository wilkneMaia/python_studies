import random
import threading
import time


def comentar(site, comentario):
    print(f'Entrando no site: {site}')
    print(f'Entrando no site: {comentario}')
    time.sleep(5)
    print(f'Dados processados no site: {site}')

comentarios = ['oi', 'olá', 'gostei', 'curti', 'muinto bom']
threads = []

for site in range(6):
    nova_theading = threading.Thread(target=comentar, args=(site, random.choice(comentarios)))
    threads.append(nova_theading)

for thread in threads:
    thread.start()
    print(f'Iniciando {thread.name}')

for thread in threads:
    thread.join()
    print(f'Finalizando {thread.name}')
