import string
import sys
import threading
from collections import Counter

from nltk.corpus import stopwords

globalCounter = Counter()
mu = threading.Lock()
pontuacao = string.punctuation
palavrasIrrelevantes = stopwords.words('portuguese')


def lerArquivo(path: str) -> list:
    with open(path, 'r', encoding='utf-8') as f:
        return f.readlines()


def filtrarTexto(split: list) -> list:
    global pontuacao
    global palavrasIrrelevantes

    semQuebraDeLinha = list(map(lambda line: line.strip(), split))
    semPontuacao = list(map(lambda line: ''.join(
        list(filter(lambda char: char not in pontuacao, line))), semQuebraDeLinha))
    minusculas = list(map(lambda line: line.lower(), semPontuacao))
    resultado = []

    for linha in minusculas:
        linhaSemStopword = ' '.join([palavra for palavra in linha.split(
        ) if palavra not in palavrasIrrelevantes]).strip()
        resultado.append(linhaSemStopword)

    return resultado


def atualizarContagem(linhas: list):
    global globalCounter
    for linha in linhas:
        if mu.acquire():
            globalCounter.update(linha.split())
            mu.release()


def contadorPalavras(path: str):
    linhas = lerArquivo(path)
    linhasLimpas = filtrarTexto(linhas)
    atualizarContagem(linhasLimpas)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f'python {sys.argv[0]} <arquivos>', file=sys.stderr)
        sys.exit(1)

    files = sys.argv[1:]
    threads = []

    for path in sys.argv[1:]:
        thread = threading.Thread(target=contadorPalavras, args=(path,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print('Contagem de palavras:', globalCounter)
