from pymongo import MongoClient
from pymongo.errors import PyMongoError

from manager import GerenciadorBiblioteca
from models import Filme, Midia, Musica, Serie, Video

# Configuração do MongoDB.
URL_MONGODB = "mongodb://localhost:27017/"
NOME_BANCO = "biblioteca_multimidia"
NOME_COLECAO = "midias"


def exibir_menu() -> None:
    """Mostra as opções disponíveis no terminal."""
    print("\n=== Gerenciador de Biblioteca Multimídia ===")
    print("1. Listar mídias")
    print("2. Buscar mídia por título")
    print("3. Remover mídia por título")
    print("4. Adicionar mídia")
    print("0. Sair")


def ler_texto(mensagem: str) -> str:
    """Pergunta ao usuário até receber um texto não vazio."""
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("O campo não pode ficar vazio.")


def ler_inteiro(mensagem: str) -> int:
    """Pergunta ao usuário até receber um número inteiro positivo."""
    while True:
        valor = input(mensagem).strip()
        try:
            numero = int(valor)
        except ValueError:
            print("Digite um número inteiro válido.")
            continue

        if numero <= 0:
            print("O número deve ser maior que zero.")
            continue
        return numero


def ler_dados_comuns() -> tuple[str, str, int, str]:
    """Lê título, caminho, ano e gênero (opcional) de qualquer mídia."""
    titulo = ler_texto("Título: ")
    caminho = ler_texto("Caminho do arquivo: ")
    ano = ler_inteiro("Ano: ")
    genero = input("Gênero (Enter para 'Não informado'): ").strip()
    if not genero:
        genero = "Não informado"
    return titulo, caminho, ano, genero


def ler_filme() -> Filme:
    titulo, caminho, ano, genero = ler_dados_comuns()
    diretor = ler_texto("Diretor: ")
    duracao = ler_inteiro("Duração (minutos): ")
    return Filme(titulo, caminho, ano, diretor, duracao, genero)


def ler_serie() -> Serie:
    titulo, caminho, ano, genero = ler_dados_comuns()
    temporada = ler_inteiro("Temporada: ")
    episodio = ler_inteiro("Episódio: ")
    return Serie(titulo, caminho, ano, temporada, episodio, genero)


def ler_musica() -> Musica:
    titulo, caminho, ano, genero = ler_dados_comuns()
    artista = ler_texto("Artista: ")
    album = ler_texto("Álbum: ")
    duracao = ler_inteiro("Duração (segundos): ")
    return Musica(titulo, caminho, ano, artista, album, duracao, genero)


def ler_video() -> Video:
    titulo, caminho, ano, genero = ler_dados_comuns()
    autor = ler_texto("Canal ou autor: ")
    duracao = ler_inteiro("Duração (minutos): ")
    return Video(titulo, caminho, ano, autor, duracao, genero)


# Liga a opção digitada à função que cria o tipo de mídia correspondente
TIPOS_DE_MIDIA = {
    "1": ("Filme", ler_filme),
    "2": ("Série", ler_serie),
    "3": ("Música", ler_musica),
    "4": ("Vídeo", ler_video),
}


def opcao_listar(gerenciador: GerenciadorBiblioteca) -> None:
    """Exibe todas as mídias cadastradas."""
    print()
    for resumo in gerenciador.listar_midias():
        print(resumo)


def opcao_buscar(gerenciador: GerenciadorBiblioteca) -> None:
    """Pede um termo ao usuário e exibe as mídias cujo título o contém."""
    termo = input("Digite o título (ou parte dele) para buscar: ").strip()
    resultados = gerenciador.buscar_por_titulo(termo)

    print()
    if not resultados:
        print("Nenhuma mídia encontrada.")
        return

    print(f"{len(resultados)} mídia(s) encontrada(s):")
    for item in resultados:
        print(item.exibir_resumo())


def opcao_remover(gerenciador: GerenciadorBiblioteca) -> None:
    """Pede o título exato, confirma com o usuário e remove a mídia."""
    titulo = input("Digite o título exato da mídia a remover: ").strip()
    confirmacao = input(f"Tem certeza que deseja remover '{titulo}'? (s/n): ").strip().lower()

    if confirmacao != "s":
        print("Remoção cancelada.")
        return

    if gerenciador.remover_por_titulo(titulo):
        print("Mídia removida com sucesso.")
    else:
        print("Mídia não encontrada.")


def opcao_adicionar(gerenciador: GerenciadorBiblioteca) -> None:
    """Pergunta o tipo de mídia, lê os dados e adiciona à biblioteca."""
    print("\nTipo de mídia:")
    for codigo, (nome, _) in TIPOS_DE_MIDIA.items():
        print(f"{codigo}. {nome}")
    print("0. Cancelar")

    escolha = input("Escolha o tipo: ").strip()
    if escolha == "0":
        print("Adição cancelada.")
        return
    if escolha not in TIPOS_DE_MIDIA:
        print("Tipo inválido.")
        return

    nome, funcao_leitura = TIPOS_DE_MIDIA[escolha]
    print(f"\nCadastrando {nome}:")
    midia: Midia = funcao_leitura()
    gerenciador.adicionar_midia(midia)
    print("Mídia adicionada com sucesso.")


def executar_menu(gerenciador: GerenciadorBiblioteca) -> None:
    """Mantém o menu em loop até o usuário escolher sair."""
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            print("Até logo!")
            break

        try:
            if opcao == "1":
                opcao_listar(gerenciador)
            elif opcao == "2":
                opcao_buscar(gerenciador)
            elif opcao == "3":
                opcao_remover(gerenciador)
            elif opcao == "4":
                opcao_adicionar(gerenciador)
            else:
                print("Opção inválida. Tente novamente.")
        except PyMongoError as erro:
            # Um erro do banco não derruba o programa: o menu continua disponível
            print(f"Erro ao acessar o banco de dados: {erro}")


def main() -> None:
    """Ponto de entrada do programa: conecta ao MongoDB e executa o menu."""
    client = MongoClient(URL_MONGODB, serverSelectionTimeoutMS=5000)

    try:
        try:
            # O ping força uma comunicação real e revela cedo se o MongoDB está fora do ar
            client.admin.command("ping")
        except PyMongoError as erro:
            print(f"Não foi possível conectar ao MongoDB em {URL_MONGODB}")
            print(erro)
            return

        colecao = client[NOME_BANCO][NOME_COLECAO]
        gerenciador = GerenciadorBiblioteca(colecao)
        executar_menu(gerenciador)
    finally:
        client.close()


if __name__ == "__main__":
    main()
