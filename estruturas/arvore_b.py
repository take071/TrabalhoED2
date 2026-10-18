"""
Módulo da Árvore B - Etapa 2
Estrutura para indexação de grande volume de clientes (~1.000 registros).
"""

class NoArvoreB:
    """Representa um nó da Árvore B com chaves e filhos."""
    def __init__(self, folha: bool = True):
        self.folha = folha
        self.chaves = []   # Lista de tuplas (id_cliente, registro_cliente)
        self.filhos = []   # Lista de referências para nós filhos


class ArvoreB:
    """
    Árvore B com grau mínimo t.
    Permite busca logarítmica e ordenação eficiente pelo ID do cliente.
    """
    def __init__(self, grau_minimo: int = 3):
        self.t = grau_minimo
        self.raiz = NoArvoreB(folha=True)
        self.total_registros = 0

    def buscar(self, id_cliente: int):
        """Busca um cliente pelo seu identificador único na Árvore B."""
        return self._buscar_no(self.raiz, id_cliente)

    def _buscar_no(self, no: NoArvoreB, id_cliente: int):
        i = 0
        while i < len(no.chaves) and id_cliente > no.chaves[i][0]:
            i += 1

        if i < len(no.chaves) and id_cliente == no.chaves[i][0]:
            return no.chaves[i][1]

        if no.folha:
            return None

        return self._buscar_no(no.filhos[i], id_cliente)

    def listar_em_ordem(self) -> list:
        """Percorre a Árvore B em ordem simétrica retornando todos os registros ordenados."""
        resultado = []
        self._percorrer_em_ordem(self.raiz, resultado)
        return resultado

    def _percorrer_em_ordem(self, no: NoArvoreB, resultado: list):
        for i in range(len(no.chaves)):
            if not no.folha:
                self._percorrer_em_ordem(no.filhos[i], resultado)
            resultado.append(no.chaves[i][1])
        if not no.folha:
            self._percorrer_em_ordem(no.filhos[len(no.chaves)], resultado)
