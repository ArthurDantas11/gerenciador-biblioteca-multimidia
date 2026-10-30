import re

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collation import Collation
from pymongo.collection import Collection

from models import Midia, criar_midia_de_dicionario


class GerenciadorBiblioteca:
    """Controla a coleção de mídias armazenadas em uma coleção do MongoDB."""

    def __init__(self, colecao: Collection):
        # A coleção do MongoDB (já conectada) é recebida de fora; o gerenciador
        # não precisa saber a URL nem o nome do banco.
        self.colecao = colecao

    def _documentos_para_midias(self, documentos) -> list[Midia]:
        """Converte documentos do MongoDB em objetos Filme, Serie, Musica, Video ou Midia."""
        midias = []
        for documento in documentos:
            midias.append(criar_midia_de_dicionario(documento))
        return midias

    def adicionar_midia(self, midia: Midia, usuario_id: str | None = None) -> str:
        """Adiciona uma nova mídia à biblioteca após validar seu tipo e retorna o ID gerado."""
        if not isinstance(midia, Midia):
            raise TypeError("O item adicionado precisa ser um objeto do tipo Midia (ou suas subclasses).")

        if usuario_id is not None:
            midia.usuario_id = usuario_id

        resultado = self.colecao.insert_one(midia.para_dicionario())
        midia.id = str(resultado.inserted_id)
        return midia.id

    def obter_midias(self, usuario_id: str | None = None) -> list[Midia]:
        """Retorna a lista de objetos de mídia cadastrados no banco (filtrando por usuário, se informado)."""
        filtro = {"usuario_id": usuario_id} if usuario_id is not None else {}
        return self._documentos_para_midias(self.colecao.find(filtro))

    def listar_midias(self, usuario_id: str | None = None) -> list[str]:
        """Retorna uma lista com os resumos formatados de todas as mídias cadastradas."""
        midias = self.obter_midias(usuario_id=usuario_id)
        if not midias:
            return ["A biblioteca está vazia no momento."]

        resumos = []
        for item in midias:
            resumos.append(item.exibir_resumo())
        return resumos

    def buscar_por_titulo(self, termo: str, usuario_id: str | None = None) -> list[Midia]:
        """Retorna uma lista de mídias cujo título contém o termo buscado (sem diferenciar maiúsculas/minúsculas)."""
        termo_limpo = termo.strip()

        # re.escape faz o termo ser tratado como texto literal (e não como padrão regex);
        # "i" ignora maiúsculas/minúsculas.
        filtro: dict = {"titulo": {"$regex": re.escape(termo_limpo), "$options": "i"}}
        if usuario_id is not None:
            filtro["usuario_id"] = usuario_id

        return self._documentos_para_midias(self.colecao.find(filtro))

    def remover_por_titulo(self, titulo: str, usuario_id: str | None = None) -> bool:
        """Remove a primeira mídia encontrada com o título exato informado. Retorna True se removeu, False caso contrário."""
        # strength=2: ignora maiúsculas/minúsculas, mas respeita acentos
        collation = Collation(locale="pt", strength=2)
        filtro: dict = {"titulo": titulo.strip()}
        if usuario_id is not None:
            filtro["usuario_id"] = usuario_id

        resultado = self.colecao.delete_one(filtro, collation=collation)
        return resultado.deleted_count > 0

    def remover_por_id(self, id_midia: str, usuario_id: str | None = None) -> bool:
        """Remove uma mídia específica pelo seu ID único do MongoDB."""
        try:
            oid = ObjectId(id_midia.strip())
        except InvalidId:
            return False

        filtro: dict = {"_id": oid}
        if usuario_id is not None:
            filtro["usuario_id"] = usuario_id

        resultado = self.colecao.delete_one(filtro)
        return resultado.deleted_count > 0



