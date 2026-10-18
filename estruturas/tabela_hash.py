"""
Objetivo:
Implementar uma Tabela Hash própria para gerenciar os países atendidos pela GlobalSIM.
A chave de busca e dispersão é o código internacional do país (ex: "BR", "IT", "US").
"""


class NoHash:
    """Nó para encadeamento separado na Tabela Hash."""
    def __init__(self, chave: str, valor: dict):
        self.chave = chave
        self.valor = valor
        self.proximo = None


class TabelaHash:
    """
    Estrutura de Tabela Hash com encadeamento separado e instrumentação
    para gerenciamento dos países atendidos pela GlobalSIM.
    """
    def __init__(self, capacidade_inicial: int = 17):
        self.capacidade = capacidade_inicial
        self.tamanho = 0  # N: total de elementos armazenados
        self.buckets = [None] * self.capacidade  # M buckets
        self.total_colisoes = 0

    def _hash(self, chave: str) -> int:
        """
        Função de dispersão polinomial (base 31) para strings curtas.
        Garante padronização em maiúsculas e resultado no intervalo [0, capacidade - 1].
        """
        chave_normalizada = str(chave).strip().upper()
        h = 0
        for caractere in chave_normalizada:
            h = (h * 31 + ord(caractere)) % self.capacidade
        return h

    def inserir(self, chave: str, valor: dict):
        """
        Insere ou atualiza um registro associado à chave.
        Trata colisões via encadeamento separado usando NoHash.
        """
        chave_normalizada = str(chave).strip().upper()
        indice = self._hash(chave_normalizada)
        atual = self.buckets[indice]

        # Caso 1: Bucket vazio
        if atual is None:
            self.buckets[indice] = NoHash(chave_normalizada, valor)
            self.tamanho += 1
            return

        # Caso 2: Bucket ocupado — verificar se a chave já existe (update)
        anterior = None
        while atual is not None:
            if atual.chave == chave_normalizada:
                atual.valor = valor  # Atualização (não conta colisão nem tamanho)
                return
            anterior = atual
            atual = atual.proximo

        # Caso 3: Colisão real detectada (nova chave no mesmo bucket)
        anterior.proximo = NoHash(chave_normalizada, valor)
        self.tamanho += 1
        self.total_colisoes += 1

    def buscar(self, chave: str) -> dict | None:
        """
        Recupera o registro associado à chave em tempo O(1) médio.
        Retorna o dicionário de dados ou None se não encontrado.
        """
        chave_normalizada = str(chave).strip().upper()
        indice = self._hash(chave_normalizada)
        atual = self.buckets[indice]

        while atual is not None:
            if atual.chave == chave_normalizada:
                return atual.valor
            atual = atual.proximo

        return None

    def remover(self, chave: str) -> bool:
        """
        Remove o registro associado à chave mantendo os ponteiros da lista.
        Retorna True se removido com sucesso, False caso contrário.
        """
        chave_normalizada = str(chave).strip().upper()
        indice = self._hash(chave_normalizada)
        atual = self.buckets[indice]
        anterior = None

        while atual is not None:
            if atual.chave == chave_normalizada:
                if anterior is None:
                    # Remove o primeiro nó do bucket
                    self.buckets[indice] = atual.proximo
                else:
                    # Remove nó intermediário ou final
                    anterior.proximo = atual.proximo
                self.tamanho -= 1
                return True

            anterior = atual
            atual = atual.proximo

        return False

    def listar_todos(self) -> list:
        """
        Retorna uma lista com todos os registros armazenados na estrutura.
        Utilizado na rota /paises e na persistência em disco (paises.json).
        """
        todos = []
        for i in range(self.capacidade):
            atual = self.buckets[i]
            while atual is not None:
                todos.append(atual.valor)
                atual = atual.proximo
        return todos

    def obter_metricas(self) -> dict:
        """
        Gera métricas de instrumentação para a rota /instrumentacao:
        - Capacidade (M)
        - Tamanho (N)
        - Fator de carga (alpha = N / M)
        - Total de colisões acumuladas
        - Distribuição detalhada dos buckets (para visualização no HTML)
        """
        distribuicao = []
        for i in range(self.capacidade):
            atual = self.buckets[i]
            chaves = []
            while atual is not None:
                chaves.append(atual.chave)
                atual = atual.proximo
            distribuicao.append({
                "indice": i,
                "total": len(chaves),
                "chaves": chaves
            })

        fator_carga = round(self.tamanho / self.capacidade, 2) if self.capacidade > 0 else 0.0

        return {
            "capacidade": self.capacidade,
            "tamanho": self.tamanho,
            "fator_carga": fator_carga,
            "total_colisoes": self.total_colisoes,
            "distribuicao_buckets": distribuicao
        }
