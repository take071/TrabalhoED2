"""
Módulo: Árvore B (Etapa 2)
Disciplina: Estruturas de Dados II - UNEB
Equipe: Arthur Felipe, Lucas Vinicius, Raphael Lopes

Objetivo:
Implementar uma Árvore B de ordem/grau mínimo t para gerenciar o grande
volume de clientes da GlobalSIM (~1.000 registros).
A chave de busca e indexação primária é o ID numérico do cliente.

Requisitos e Orientações:
1. Nós com no máximo 2t - 1 chaves e no mínimo t - 1 chaves (exceto a raiz).
2. Algoritmo de busca logarítmica O(log n).
3. Inserção balanceada com divisão de nó (split) quando um nó atinge a capacidade máxima.
4. Percurso em ordem para listagem ordenada dos clientes.
"""


class NoArvoreB:
    """
    Representação de um nó na Árvore B.
    """
    def __init__(self, folha: bool = True):
        self.folha = folha
        # Lista ordenada de chaves ou tuplas (id_cliente, dados_cliente)
        self.chaves = []
        # Lista de referências para os nós filhos
        self.filhos = []


class ArvoreB:
    """
    Estrutura da Árvore B para indexação e busca balanceada de clientes.
    """
    def __init__(self, grau_minimo: int = 3):
        # Grau mínimo t da árvore (determina número mínimo e máximo de chaves por nó)
        self.t = grau_minimo
        self.raiz = NoArvoreB(folha=True)
        self.total_registros = 0

    def buscar(self, id_cliente: int):
        """
        Realiza busca recursiva ou iterativa a partir da raiz pelo ID do cliente.
        Retorna o registro do cliente ou None se não encontrado.
        """
        # TODO: Implementar busca na Árvore B
        pass

    def dividir_filho(self, pai: NoArvoreB, indice: int, filho_cheio: NoArvoreB):
        """
        Divide um nó filho que atingiu 2t - 1 chaves, promovendo a chave mediana
        para o nó pai.
        """
        # TODO: Implementar divisão de nó cheio (split)
        pass

    def inserir_nao_cheio(self, no: NoArvoreB, id_cliente: int, dados: dict):
        """
        Auxiliar recursivo para inserção quando o nó atual não está cheio.
        """
        # TODO: Implementar inserção descendo pelos nós apropriados
        pass

    def inserir(self, id_cliente: int, dados: dict):
        """
        Insere um novo cliente na Árvore B.
        Caso a raiz esteja cheia, cria uma nova raiz e divide a anterior.
        """
        # TODO: Implementar inserção principal
        pass

    def listar_em_ordem(self) -> list:
        """
        Retorna todos os registros em ordem crescente de ID do cliente.
        """
        # TODO: Implementar percurso em-ordem
        return []
