import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

# Chave secreta usada para assinar os tokens JWT.
# Em produção, ela deve vir de uma variável de ambiente (ex: arquivo .env).
CHAVE_SECRETA = os.getenv("JWT_CHAVE_SECRETA", "chave-secreta-desenvolvimento-local-2026")
ALGORITMO = "HS256"
TEMPO_EXPIRACAO_HORAS = 24


def gerar_hash_senha(senha: str) -> str:
    """Transforma uma senha em texto puro em um hash seguro usando bcrypt."""
    # O bcrypt trabalha com bytes, então convertemos a string com .encode("utf-8")
    senha_bytes = senha.encode("utf-8")
    sal = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(senha_bytes, sal)
    # Devolvemos como string (str) para salvar facilmente no MongoDB
    return hash_bytes.decode("utf-8")


def verificar_senha(senha_digitada: str, hash_salvo: str) -> bool:
    """Verifica se a senha digitada no login corresponde ao hash salvo no banco."""
    senha_bytes = senha_digitada.encode("utf-8")
    hash_bytes = hash_salvo.encode("utf-8")
    return bcrypt.checkpw(senha_bytes, hash_bytes)


def criar_token_acesso(usuario_id: str, email: str) -> str:
    """Cria um token JWT assinado contendo o ID, o e-mail e a data de expiração."""
    expiracao = datetime.now(timezone.utc) + timedelta(hours=TEMPO_EXPIRACAO_HORAS)
    dados_token = {
        "sub": usuario_id,  # "sub" (subject) é o padrão JWT para o identificador do usuário
        "email": email,
        "exp": expiracao,   # "exp" (expiration) define até quando o token é válido
    }
    return jwt.encode(dados_token, CHAVE_SECRETA, algorithm=ALGORITMO)


def validar_token_acesso(token: str) -> dict | None:
    """
    Decodifica e valida um token JWT.
    Retorna o dicionário de dados do token se for válido, ou None se for inválido/expirado.
    """
    try:
        dados = jwt.decode(token, CHAVE_SECRETA, algorithms=[ALGORITMO])
        return dados
    except jwt.PyJWTError:
        return None
