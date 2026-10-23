class Midia:
    """Representa um item genérico de mídia na biblioteca."""

    def __init__(self, titulo: str, caminho_arquivo: str, ano: int, genero: str = "Não informado"):
        self.titulo = titulo
        self.caminho_arquivo = caminho_arquivo
        self.ano = ano
        self.genero = genero

    def exibir_resumo(self) -> str:
        """Retorna uma string formatada com os dados básicos da mídia."""
        return f"[{self.genero}] {self.titulo} ({self.ano}) -> Local: {self.caminho_arquivo}"

    def para_dicionario(self) -> dict:
        """Converte os dados básicos da mídia em um dicionário para salvar em JSON."""
        return {
            "tipo": "Midia",
            "titulo": self.titulo,
            "caminho_arquivo": self.caminho_arquivo,
            "ano": self.ano,
            "genero": self.genero,
        }


class Filme(Midia):
    """Representa um filme na biblioteca."""

    def __init__(
        self,
        titulo: str,
        caminho_arquivo: str,
        ano: int,
        diretor: str,
        duracao_minutos: int,
        genero: str = "Não informado",
    ):
        super().__init__(titulo, caminho_arquivo, ano, genero)
        self.diretor = diretor
        self.duracao_minutos = duracao_minutos

    def exibir_resumo(self) -> str:
        return (
            f"[FILME | {self.genero}] {self.titulo} ({self.ano}) - "
            f"Dir: {self.diretor} ({self.duracao_minutos} min) -> Local: {self.caminho_arquivo}"
        )

    def para_dicionario(self) -> dict:
        dados = super().para_dicionario()
        dados["tipo"] = "Filme"
        dados["diretor"] = self.diretor
        dados["duracao_minutos"] = self.duracao_minutos
        return dados


class Serie(Midia):
    """Representa um episódio de série na biblioteca."""

    def __init__(
        self,
        titulo: str,
        caminho_arquivo: str,
        ano: int,
        temporada: int,
        episodio: int,
        genero: str = "Não informado",
    ):
        super().__init__(titulo, caminho_arquivo, ano, genero)
        self.temporada = temporada
        self.episodio = episodio

    def exibir_resumo(self) -> str:
        # :02d formata o número com 2 dígitos (ex: 1 vira 01 -> S01E02)
        return (
            f"[SÉRIE | {self.genero}] {self.titulo} S{self.temporada:02d}E{self.episodio:02d} "
            f"({self.ano}) -> Local: {self.caminho_arquivo}"
        )

    def para_dicionario(self) -> dict:
        dados = super().para_dicionario()
        dados["tipo"] = "Serie"
        dados["temporada"] = self.temporada
        dados["episodio"] = self.episodio
        return dados


class Musica(Midia):
    """Representa uma faixa de música na biblioteca."""

    def __init__(
        self,
        titulo: str,
        caminho_arquivo: str,
        ano: int,
        artista: str,
        album: str,
        duracao_segundos: int,
        genero: str = "Não informado",
    ):
        super().__init__(titulo, caminho_arquivo, ano, genero)
        self.artista = artista
        self.album = album
        self.duracao_segundos = duracao_segundos

    def exibir_resumo(self) -> str:
        return (
            f"[MÚSICA | {self.genero}] {self.artista} - {self.titulo} "
            f"(Álbum: {self.album}, {self.ano}, {self.duracao_segundos}s) -> Local: {self.caminho_arquivo}"
        )

    def para_dicionario(self) -> dict:
        dados = super().para_dicionario()
        dados["tipo"] = "Musica"
        dados["artista"] = self.artista
        dados["album"] = self.album
        dados["duracao_segundos"] = self.duracao_segundos
        return dados


class Video(Midia):
    """Representa um vídeo geral (aulas, clipes, gravações) na biblioteca."""

    def __init__(
        self,
        titulo: str,
        caminho_arquivo: str,
        ano: int,
        canal_ou_autor: str,
        duracao_minutos: int,
        genero: str = "Não informado",
    ):
        super().__init__(titulo, caminho_arquivo, ano, genero)
        self.canal_ou_autor = canal_ou_autor
        self.duracao_minutos = duracao_minutos

    def exibir_resumo(self) -> str:
        return (
            f"[VÍDEO | {self.genero}] {self.titulo} ({self.ano}) - "
            f"Autor/Canal: {self.canal_ou_autor} ({self.duracao_minutos} min) -> Local: {self.caminho_arquivo}"
        )

    def para_dicionario(self) -> dict:
        dados = super().para_dicionario()
        dados["tipo"] = "Video"
        dados["canal_ou_autor"] = self.canal_ou_autor
        dados["duracao_minutos"] = self.duracao_minutos
        return dados


def criar_midia_de_dicionario(dados: dict) -> Midia:
    """Reconstrói o objeto correto (Filme, Serie, Musica, Video ou Midia) a partir de um dicionário."""
    tipo = dados.get("tipo", "Midia")
    genero = dados.get("genero", "Não informado")

    if tipo == "Filme":
        return Filme(
            titulo=dados["titulo"],
            caminho_arquivo=dados["caminho_arquivo"],
            ano=dados["ano"],
            diretor=dados["diretor"],
            duracao_minutos=dados["duracao_minutos"],
            genero=genero,
        )
    elif tipo == "Serie":
        return Serie(
            titulo=dados["titulo"],
            caminho_arquivo=dados["caminho_arquivo"],
            ano=dados["ano"],
            temporada=dados["temporada"],
            episodio=dados["episodio"],
            genero=genero,
        )
    elif tipo == "Musica":
        return Musica(
            titulo=dados["titulo"],
            caminho_arquivo=dados["caminho_arquivo"],
            ano=dados["ano"],
            artista=dados["artista"],
            album=dados["album"],
            duracao_segundos=dados["duracao_segundos"],
            genero=genero,
        )
    elif tipo == "Video":
        return Video(
            titulo=dados["titulo"],
            caminho_arquivo=dados["caminho_arquivo"],
            ano=dados["ano"],
            canal_ou_autor=dados["canal_ou_autor"],
            duracao_minutos=dados["duracao_minutos"],
            genero=genero,
        )
    else:
        return Midia(
            titulo=dados["titulo"],
            caminho_arquivo=dados["caminho_arquivo"],
            ano=dados["ano"],
            genero=genero,
        )

