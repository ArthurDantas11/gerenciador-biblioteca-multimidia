# Gerenciador de Biblioteca Multimídia

Projeto em Python, desenvolvido por etapas para aprendizado, que cataloga filmes, séries, músicas e vídeos armazenados no computador. Possui uma interface de terminal (CLI), uma API REST com **FastAPI** e usa o **MongoDB** para guardar os dados.

## Funcionalidades

- Autenticação de usuários com **bcrypt** (hash de senhas) e **JWT** (Bearer Token)
- Biblioteca individual por usuário na API REST
- Adicionar mídias dos tipos **Filme**, **Série**, **Música** e **Vídeo**
- Listar todas as mídias cadastradas
- Buscar por título (parcial, sem diferenciar maiúsculas e minúsculas)
- Remover por título (no CLI) ou por ID único do MongoDB (na API REST)

## Pré-requisitos

- Python 3.10 ou superior (desenvolvido e testado com Python 3.14)
- MongoDB em execução localmente (`mongodb://localhost:27017/`)

## Instalação

```powershell
pip install -r requirements.txt
```

## Como executar

### 1. Modo Terminal (CLI)

```powershell
python main.py
```

### 2. Modo API REST (FastAPI)

```powershell
uvicorn api:app --reload
```

Com o servidor rodando, acesse no navegador:
- **API:** `http://127.0.0.1:8000/midias`
- **Documentação interativa (Swagger UI):** `http://127.0.0.1:8000/docs`

### Rotas da API

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| `GET` | `/` | Pública | Verifica se a API está online |
| `POST` | `/usuarios/registro` | Pública | Cria uma nova conta de usuário |
| `POST` | `/usuarios/login` | Pública | Autentica o usuário e retorna o Token JWT |
| `GET` | `/midias` | Bearer Token | Lista as mídias do usuário logado (ou filtra com `?titulo=...`) |
| `POST` | `/midias` | Bearer Token | Cadastra uma nova mídia vinculada ao usuário logado |
| `DELETE` | `/midias/{id_midia}` | Bearer Token | Remove uma mídia do usuário logado pelo ID |

## Estrutura do projeto

| Arquivo | Função |
|---|---|
| `api.py` | API REST em FastAPI com autenticação JWT, validação Pydantic e CORS |
| `auth.py` | Funções de segurança: hash de senhas com `bcrypt` e tokens `JWT` |
| `main.py` | Ponto de entrada CLI: conexão com o MongoDB e menu de terminal |
| `manager.py` | Classe `GerenciadorBiblioteca`: adicionar, listar, buscar e remover mídias |
| `models.py` | Classes `Midia`, `Filme`, `Serie`, `Musica` e `Video`, e conversão entre objetos e dicionários |

## Configuração

A URL do MongoDB, o nome do banco e o nome da coleção estão nas constantes no início de `main.py` e `api.py`:

```python
URL_MONGODB = "mongodb://localhost:27017/"
NOME_BANCO = "biblioteca_multimidia"
NOME_COLECAO = "midias"
```

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).
