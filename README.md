# Gerenciador de Biblioteca Multimídia

Projeto em Python, desenvolvido por etapas para aprendizado, que cataloga filmes, séries, músicas e vídeos armazenados no computador. Possui uma interface de terminal (CLI) e usa o MongoDB para guardar os dados.

## Funcionalidades

- Adicionar mídias dos tipos **Filme**, **Série**, **Música** e **Vídeo**
- Listar todas as mídias cadastradas
- Buscar por título (parcial, sem diferenciar maiúsculas e minúsculas)
- Remover por título (exato, sem diferenciar maiúsculas e minúsculas, respeitando acentos)

## Pré-requisitos

- Python 3.9 ou superior (desenvolvido e testado com Python 3.14)
- MongoDB em execução localmente (`mongodb://localhost:27017/`)

## Instalação

```powershell
pip install -r requirements.txt
```

## Como executar

```powershell
python main.py
```

O programa conecta ao MongoDB, usa o banco `biblioteca_multimidia` e a coleção `midias` (criada automaticamente no primeiro cadastro) e abre o menu no terminal. Todas as operações são gravadas no banco imediatamente.

Se o MongoDB estiver fora do ar, o programa informa o erro e encerra.

## Estrutura do projeto

| Arquivo | Função |
|---|---|
| `main.py` | Ponto de entrada: conexão com o MongoDB e menu de terminal |
| `manager.py` | Classe `GerenciadorBiblioteca`: adicionar, listar, buscar e remover mídias |
| `models.py` | Classes `Midia`, `Filme`, `Serie`, `Musica` e `Video`, e a conversão entre objetos e dicionários |

## Configuração

A URL do MongoDB, o nome do banco e o nome da coleção estão nas constantes no início do `main.py`:

```python
URL_MONGODB = "mongodb://localhost:27017/"
NOME_BANCO = "biblioteca_multimidia"
NOME_COLECAO = "midias"
```

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).
