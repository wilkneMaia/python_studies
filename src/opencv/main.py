from collections import Counter

import cv2
import numpy as np


if __name__ == "__main__":

    def find_dominant_color(image):
        # Converta a imagem para o espaço de cores HSV
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Encontre a cor predominante na imagem
        pixel_colors = image_hsv.reshape(-1, image_hsv.shape[-1])
        counter = Counter(map(tuple, pixel_colors))
        most_common_color = counter.most_common(1)[0][0]

        # Crie uma faixa de cor HSV com base na cor predominante e uma pequena tolerância
        lower_bound = np.array([most_common_color[0] - 5, 100, 100])
        upper_bound = np.array([most_common_color[0] + 5, 255, 255])

        return lower_bound, upper_bound

    # Carregue a imagem (substitua 'imagem.jpg' pelo caminho da sua imagem)
    image = cv2.imread('Post_it.jpeg')

    # Encontre a cor predominante e calcule a faixa de cor
    lower_color, upper_color = find_dominant_color(image)

    # Formate a faixa de cor no formato desejado
    color_range = f'"cor": ({list(lower_color)}, {list(upper_color)})'

    # Exiba a faixa de cor
    print(color_range)

    # Dicionário de cores e seus valores HSV correspondentes
    cores = {
        "vermelho": ([0, 100, 100], [10, 255, 255]),
        "verde": ([35, 100, 100], [85, 255, 255]),
        "azul": ([100, 100, 100], [130, 255, 255]),
        "amarelo": ([20, 100, 100], [35, 255, 255]),
        "amarelo2": ([17, 100, 100], [27, 255, 255]),
    }

    # Função para identificar a cor em uma imagem e retornar o nome da cor
    def identificar_cor(imagem, cores):
        # Converter a imagem para o espaço de cores HSV
        imagem_hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)

        # Percorrer o dicionário de cores
        for cor, (limite_inferior, limite_superior) in cores.items():
            # Criar uma máscara para a cor alvo
            mascara = cv2.inRange(imagem_hsv, np.array(
                limite_inferior), np.array(limite_superior))

            # Verificar se a máscara contém pixels brancos (cor encontrada)
            if cv2.countNonZero(mascara) > 0:
                return cor

        # Se nenhuma cor for encontrada, retornar "desconhecida"
        return "desconhecida"

    # Carregar a imagem
    imagem = cv2.imread('Post_it.jpeg')

    # Identificar a cor na imagem
    cor_identificada = identificar_cor(imagem, cores)

    # Exibir o nome da cor identificada
    print(f"A cor identificada na imagem é: {cor_identificada}")
