"""
Módulo da Tabela Hash - Etapa 1
Implementação manual da Tabela Hash para gerenciamento de países atendidos.
Inclui tratamento de colisões e métricas de instrumentação.
"""

class NoHash:
    """Nó para encadeamento de elementos com colisões na Tabela Hash."""
    def __init__(self, chave: str, valor: dict):
        self.chave = chave
        self.valor = valor
        self.proximo = None


class TabelaHash:
    """
    Tabela Hash implementada para o domínio de países atendidos da GlobalSIM.
    Utiliza encadeamento separado para tratamento de colisões.
    """
    def __init__(self, capacidade_inicial: int = 17):
        self.capacidade = capacidade_inicial
        self.tamanho = 0
        self.buckets = [None] * self.capacidade
        self.total_colisoes = 0

    def _funcao_hash(self, chave: str) -> int:
        """
        Função de espalhamento baseada em método polinomial com base prima (31).
        Gera índices bem distribuídos para códigos de países (ex: 'BR', 'US', 'IT').
        """
        hash_val = 0
        for char in str(chave).strip().upper():
            hash_val = (hash_val * 31 + ord(char)) % self.capacidade
        return hash_val

    def inserir(self, chave: str, valor: dict) -> None:
        """Insere ou atualiza um registro associado à chave."""
        chave = str(chave).strip().upper()
        indice = self._funcao_hash(chave)
        atual = self.buckets[indice]

        # Caso bucket vazio
        if atual is None:
            self.buckets[indice] = NoHash(chave, valor)
            self.tamanho += 1
            return

        # Tratar colisão ou atualização
        colidiu = False
        anterior = None
        while atual is not None:
            if atual.chave == chave:
                atual.valor = valor  # Atualiza valor existente
                return
            anterior = atual
            atual = atual.proximo
            colidiu = True

        if colidiu:
            self.total_colisoes += 1

        anterior.proximo = NoHash(chave, valor)
        self.tamanho += 1

    def buscar(self, chave: str):
        """Busca um país pelo seu código (chave). Retorna dict ou None."""
        chave = str(chave).strip().upper()
        indice = self._funcao_hash(chave)
        atual = self.buckets[indice]
        while atual is not None:
            if atual.chave == chave:
                return atual.valor
            atual = atual.proximo
        return None

    def remover(self, chave: str) -> bool:
        """Remove o país da tabela pela chave. Retorna True se removido, False caso contrário."""
        chave = str(chave).strip().upper()
        indice = self._funcao_hash(chave)
        atual = self.buckets[indice]
        anterior = None

        while atual is not None:
            if atual.chave == chave:
                if anterior is None:
                    self.buckets[indice] = atual.proximo
                else:
                    anterior.proximo = atual.proximo
                self.tamanho -= 1
                return True
            anterior = atual
            atual = atual.proximo
        return False

    def listar_todos(self) -> list:
        """Retorna uma lista com todos os registros armazenados."""
        elementos = []
        for bucket in self.buckets:
            atual = bucket
            while atual is not None:
                elementos.append(atual.valor)
                atual = atual.proximo
        return elementos

    def obter_metricas(self) -> dict:
        """Retorna métricas de instrumentação para análise da estrutura."""
        buckets_ocupados = sum(1 for b in self.buckets if b is not None)
        tamanhos_buckets = []
        for i, b in enumerate(self.buckets):
            qtd = 0
            atual = b
            while atual:
                qtd += 1
                atual = atual.proximo
            tamanhos_buckets.append({"indice": i, "quantidade": qtd})

        fator_carga = self.tamanho / self.capacidade if self.capacidade > 0 else 0
        return {
            "capacidade": self.capacidade,
            "total_elementos": self.tamanho,
            "fator_carga": round(fator_carga, 3),
            "buckets_ocupados": buckets_ocupados,
            "total_colisoes": self.total_colisoes,
            "distribuicao": tamanhos_buckets
        }
