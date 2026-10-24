from typing import Literal

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient

from manager import GerenciadorBiblioteca
from models import Filme, Midia, Musica, Serie, Video

# 1. Configuração da conexão com o MongoDB
URL_MONGODB = "mongodb://localhost:27017/"
NOME_BANCO = "biblioteca_multimidia"
NOME_COLECAO = "midias"

client = MongoClient(URL_MONGODB, serverSelectionTimeoutMS=5000)
colecao = client[NOME_BANCO][NOME_COLECAO]
gerenciador = GerenciadorBiblioteca(colecao)

# 2. Criação da aplicação FastAPI
app = FastAPI(
    title="API - Gerenciador de Biblioteca Multimídia",
    description="API REST para gerenciar filmes, séries, músicas e vídeos no MongoDB.",
    version="1.0.0",
)

# 2.1 Configuração de CORS (permite que o front-end Next.js acesse a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. Modelo de Entrada (Pydantic) para validar o JSON enviado no POST /midias
class MidiaEntrada(BaseModel):
    """Define e valida os dados necessários para cadastrar uma nova mídia."""

    tipo: Literal["Filme", "Serie", "Musica", "Video"]
    titulo: str = Field(..., min_length=1, examples=["Interestelar"])
    caminho_arquivo: str = Field(..., min_length=1, examples=["C:/Filmes/interestelar.mkv"])
    ano: int = Field(..., gt=0, examples=[2014])
    genero: str = Field(default="Não informado", examples=["Ficção Científica"])

    # Campos específicos opcionais (exigidos conforme o 'tipo' escolhido)
    diretor: str | None = Field(default=None, examples=["Christopher Nolan"])
    duracao_minutos: int | None = Field(default=None, gt=0, examples=[169])
    temporada: int | None = Field(default=None, gt=0, examples=[1])
    episodio: int | None = Field(default=None, gt=0, examples=[1])
    artista: str | None = Field(default=None, examples=["Pink Floyd"])
    album: str | None = Field(default=None, examples=["The Dark Side of the Moon"])
    duracao_segundos: int | None = Field(default=None, gt=0, examples=[413])
    canal_ou_autor: str | None = Field(default=None, examples=["Curso de Python"])


# 4. Rota inicial (Health Check)
@app.get("/")
def rota_inicial() -> dict:
    """Verifica se a API está no ar."""
    return {"mensagem": "API do Gerenciador de Biblioteca Multimídia funcionando!"}


# 5. Rota para listar todas as mídias ou buscar por título (GET /midias)
@app.get("/midias")
def listar_midias(titulo: str | None = None) -> list[dict]:
    """
    Lista as mídias cadastradas.
    Se o parâmetro 'titulo' for informado na URL (?titulo=...), filtra pelo título.
    """
    if titulo:
        midias = gerenciador.buscar_por_titulo(titulo)
    else:
        midias = gerenciador.obter_midias()

    return [item.para_dicionario() for item in midias]


# 6. Rota para cadastrar uma nova mídia (POST /midias)
@app.post("/midias", status_code=status.HTTP_201_CREATED)
def adicionar_midia(dados: MidiaEntrada) -> dict:
    """Recebe os dados de uma mídia em JSON, valida e salva no MongoDB."""
    nova_midia: Midia

    if dados.tipo == "Filme":
        if not dados.diretor or dados.duracao_minutos is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para o tipo 'Filme', os campos 'diretor' e 'duracao_minutos' são obrigatórios.",
            )
        nova_midia = Filme(
            titulo=dados.titulo,
            caminho_arquivo=dados.caminho_arquivo,
            ano=dados.ano,
            diretor=dados.diretor,
            duracao_minutos=dados.duracao_minutos,
            genero=dados.genero,
        )

    elif dados.tipo == "Serie":
        if dados.temporada is None or dados.episodio is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para o tipo 'Serie', os campos 'temporada' e 'episodio' são obrigatórios.",
            )
        nova_midia = Serie(
            titulo=dados.titulo,
            caminho_arquivo=dados.caminho_arquivo,
            ano=dados.ano,
            temporada=dados.temporada,
            episodio=dados.episodio,
            genero=dados.genero,
        )

    elif dados.tipo == "Musica":
        if not dados.artista or not dados.album or dados.duracao_segundos is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para o tipo 'Musica', os campos 'artista', 'album' e 'duracao_segundos' são obrigatórios.",
            )
        nova_midia = Musica(
            titulo=dados.titulo,
            caminho_arquivo=dados.caminho_arquivo,
            ano=dados.ano,
            artista=dados.artista,
            album=dados.album,
            duracao_segundos=dados.duracao_segundos,
            genero=dados.genero,
        )

    elif dados.tipo == "Video":
        if not dados.canal_ou_autor or dados.duracao_minutos is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para o tipo 'Video', os campos 'canal_ou_autor' e 'duracao_minutos' são obrigatórios.",
            )
        nova_midia = Video(
            titulo=dados.titulo,
            caminho_arquivo=dados.caminho_arquivo,
            ano=dados.ano,
            canal_ou_autor=dados.canal_ou_autor,
            duracao_minutos=dados.duracao_minutos,
            genero=dados.genero,
        )

    gerenciador.adicionar_midia(nova_midia)
    return nova_midia.para_dicionario()


# 7. Rota para remover uma mídia pelo seu ID único do MongoDB (DELETE /midias/{id_midia})
@app.delete("/midias/{id_midia}")
def remover_midia(id_midia: str) -> dict:
    """Remove uma mídia do MongoDB usando seu ID único."""
    removido = gerenciador.remover_por_id(id_midia)
    if not removido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mídia com ID '{id_midia}' não encontrada.",
        )

    return {"mensagem": "Mídia removida com sucesso.", "id_removido": id_midia}
