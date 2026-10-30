from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from pymongo import MongoClient

from auth import criar_token_acesso, gerar_hash_senha, validar_token_acesso, verificar_senha
from manager import GerenciadorBiblioteca
from models import Filme, Midia, Musica, Serie, Video

# 1. Configuração da conexão com o MongoDB
URL_MONGODB = "mongodb://localhost:27017/"
NOME_BANCO = "biblioteca_multimidia"
NOME_COLECAO = "midias"
NOME_COLECAO_USUARIOS = "usuarios"

client = MongoClient(URL_MONGODB, serverSelectionTimeoutMS=5000)
banco = client[NOME_BANCO]
colecao = banco[NOME_COLECAO]
colecao_usuarios = banco[NOME_COLECAO_USUARIOS]
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


# 2.2 Esquema de segurança Bearer Token (ativa o botão "Authorize" no /docs)
seguranca_bearer = HTTPBearer()


def obter_usuario_logado(
    credenciais: HTTPAuthorizationCredentials = Depends(seguranca_bearer),
) -> str:
    """
    Valida o Token JWT enviado no cabeçalho Authorization: Bearer <token>
    e retorna o ID do usuário autenticado (usuario_id).
    """
    dados_token = validar_token_acesso(credenciais.credentials)
    if not dados_token or "sub" not in dados_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado. Faça login novamente.",
        )
    return str(dados_token["sub"])


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


# 3.1 Modelos de Entrada (Pydantic) para Registro e Login de Usuários
class UsuarioRegistro(BaseModel):
    """Dados necessários para criar uma nova conta de usuário."""

    nome: str = Field(..., min_length=2, examples=["Arthur Dantas"])
    email: str = Field(..., min_length=5, examples=["arthur@email.com"])
    senha: str = Field(..., min_length=6, examples=["minha_senha_123"])


class UsuarioLogin(BaseModel):
    """Dados necessários para autenticar um usuário."""

    email: str = Field(..., min_length=5, examples=["arthur@email.com"])
    senha: str = Field(..., min_length=6, examples=["minha_senha_123"])


# 4. Rota inicial (Health Check)
@app.get("/")
def rota_inicial() -> dict:
    """Verifica se a API está no ar."""
    return {"mensagem": "API do Gerenciador de Biblioteca Multimídia funcionando!"}


# 4.1 Rotas de Autenticação de Usuários (Registro e Login)
@app.post("/usuarios/registro", status_code=status.HTTP_201_CREATED)
def registrar_usuario(dados: UsuarioRegistro) -> dict:
    """Cadastra um novo usuário no MongoDB com senha criptografada."""
    email_limpo = dados.email.strip().lower()

    if "@" not in email_limpo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe um endereço de e-mail válido.",
        )

    usuario_existente = colecao_usuarios.find_one({"email": email_limpo})
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este e-mail já está cadastrado.",
        )

    novo_usuario = {
        "nome": dados.nome.strip(),
        "email": email_limpo,
        "senha_hash": gerar_hash_senha(dados.senha),
    }
    resultado = colecao_usuarios.insert_one(novo_usuario)

    return {
        "id": str(resultado.inserted_id),
        "nome": novo_usuario["nome"],
        "email": novo_usuario["email"],
        "mensagem": "Usuário cadastrado com sucesso!",
    }


@app.post("/usuarios/login")
def login_usuario(dados: UsuarioLogin) -> dict:
    """Verifica e-mail e senha e retorna um token JWT de acesso."""
    email_limpo = dados.email.strip().lower()
    usuario = colecao_usuarios.find_one({"email": email_limpo})

    if not usuario or not verificar_senha(dados.senha, usuario["senha_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )

    usuario_id = str(usuario["_id"])
    token = criar_token_acesso(usuario_id=usuario_id, email=usuario["email"])

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario_id,
            "nome": usuario["nome"],
            "email": usuario["email"],
        },
    }


# 5. Rota para listar todas as mídias do usuário logado ou buscar por título (GET /midias)
@app.get("/midias")
def listar_midias(
    titulo: str | None = None,
    usuario_id: str = Depends(obter_usuario_logado),
) -> list[dict]:
    """
    Lista as mídias cadastradas pelo usuário logado.
    Se o parâmetro 'titulo' for informado na URL (?titulo=...), filtra pelo título.
    """
    if titulo:
        midias = gerenciador.buscar_por_titulo(titulo, usuario_id=usuario_id)
    else:
        midias = gerenciador.obter_midias(usuario_id=usuario_id)

    return [item.para_dicionario() for item in midias]


# 6. Rota para cadastrar uma nova mídia vinculada ao usuário logado (POST /midias)
@app.post("/midias", status_code=status.HTTP_201_CREATED)
def adicionar_midia(
    dados: MidiaEntrada,
    usuario_id: str = Depends(obter_usuario_logado),
) -> dict:
    """Recebe os dados de uma mídia em JSON, valida e salva no MongoDB vinculada ao usuário logado."""
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

    gerenciador.adicionar_midia(nova_midia, usuario_id=usuario_id)
    return nova_midia.para_dicionario()


# 7. Rota para remover uma mídia do usuário logado pelo ID (DELETE /midias/{id_midia})
@app.delete("/midias/{id_midia}")
def remover_midia(
    id_midia: str,
    usuario_id: str = Depends(obter_usuario_logado),
) -> dict:
    """Remove uma mídia do usuário logado no MongoDB usando seu ID único."""
    removido = gerenciador.remover_por_id(id_midia, usuario_id=usuario_id)
    if not removido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mídia com ID '{id_midia}' não encontrada na sua biblioteca.",
        )

    return {"mensagem": "Mídia removida com sucesso.", "id_removido": id_midia}
