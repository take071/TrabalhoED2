"""
Objetivo:
Implementar uma Árvore B própria para indexar os clientes (e seus eSIMs) da GlobalSIM.
A chave de busca é o ID único do cliente (inteiro) e o valor é o registro completo
do cliente (dict).

Definição utilizada (grau mínimo t, conforme Cormen et al.):
- Todo nó, exceto a raiz, possui no mínimo t - 1 chaves.
- Todo nó possui no máximo 2t - 1 chaves (ou seja, no máximo 2t filhos).
- Um nó interno com k chaves possui exatamente k + 1 filhos.
- Todas as folhas estão no mesmo nível.

A inserção é feita em uma única passagem descendente (divisão preventiva): qualquer
nó cheio encontrado no caminho é dividido antes de descer. Quando a raiz se divide,
a altura da árvore cresce em 1.

Listas Python são usadas apenas DENTRO de cada nó (chaves, valores e filhos). A
navegação entre nós, a busca e as divisões são feitas pela própria Árvore B.
"""

from collections import deque


class NoB:
    """Nó da Árvore B: chaves ordenadas, valores associados e ponteiros para filhos."""

    def __init__(self, id_no: int, folha: bool):
        self.id = id_no          # identificador apenas para visualização/instrumentação
        self.folha = folha
        self.chaves = []         # IDs de clientes, em ordem crescente
        self.valores = []        # registros completos (mesmo índice de self.chaves)
        self.filhos = []         # len(filhos) == len(chaves) + 1 nos nós internos


class ArvoreB:
    """
    Árvore B com instrumentação para gerenciamento dos clientes da GlobalSIM.
    """

    def __init__(self, grau_minimo: int = 3):
        if grau_minimo < 2:
            raise ValueError("O grau mínimo da Árvore B deve ser >= 2.")

        self.t = grau_minimo
        self.max_chaves = 2 * grau_minimo - 1
        self.min_chaves = grau_minimo - 1

        self._proximo_id_no = 1
        self.raiz = self._novo_no(folha=True)
        self.tamanho = 0                      # N: total de chaves armazenadas

        # IDs na ordem em que foram inseridos. Não participa de nenhuma busca: serve
        # apenas para a persistência, pois reinserir os registros nessa mesma ordem
        # reconstrói exatamente a mesma árvore (a inserção é determinística).
        self.ordem_insercao = []

        # Instrumentação acumulada
        self.total_divisoes = 0
        self.total_buscas = 0
        self.total_acessos_busca = 0          # nós visitados somados em todas as buscas
        self.total_comparacoes_busca = 0
        self.historico_divisoes = deque(maxlen=15)

        # Instrumentação da última operação
        self.ultima_busca = None              # dict com chave, caminho, acessos, comparações
        self.ultima_insercao = None           # dict com chave, acessos, divisões

    # ------------------------------------------------------------------
    # Auxiliares internos
    # ------------------------------------------------------------------
    def _novo_no(self, folha: bool) -> NoB:
        no = NoB(self._proximo_id_no, folha)
        self._proximo_id_no += 1
        return no

    @staticmethod
    def _normalizar_chave(chave) -> int:
        return int(chave)

    def _localizar(self, chave: int):
        """
        Desce a árvore procurando a chave.
        Retorna (no, indice, caminho, comparacoes); `no` é None quando não encontrada.
        `caminho` é a lista de IDs dos nós visitados da raiz até o nó final.
        """
        no = self.raiz
        caminho = []
        comparacoes = 0

        while True:
            caminho.append(no.id)

            i = 0
            n = len(no.chaves)
            while i < n and chave > no.chaves[i]:
                comparacoes += 1
                i += 1
            if i < n:
                comparacoes += 1  # comparação que encerrou a varredura (== ou <)
                if chave == no.chaves[i]:
                    return no, i, caminho, comparacoes

            if no.folha:
                return None, -1, caminho, comparacoes

            no = no.filhos[i]

    # ------------------------------------------------------------------
    # Busca
    # ------------------------------------------------------------------
    def buscar(self, chave) -> dict | None:
        """
        Recupera o registro do cliente pelo ID em O(t · log_t N).
        Retorna o dicionário do cliente ou None se não existir.
        Atualiza a instrumentação da última busca.
        """
        chave = self._normalizar_chave(chave)
        no, i, caminho, comparacoes = self._localizar(chave)

        self.total_buscas += 1
        self.total_acessos_busca += len(caminho)
        self.total_comparacoes_busca += comparacoes
        self.ultima_busca = {
            "chave": chave,
            "encontrada": no is not None,
            "caminho": caminho,
            "acessos": len(caminho),
            "comparacoes": comparacoes,
        }

        return no.valores[i] if no is not None else None

    def contem(self, chave) -> bool:
        """Verifica existência da chave sem alterar a instrumentação."""
        return self._localizar(self._normalizar_chave(chave))[0] is not None

    # ------------------------------------------------------------------
    # Inserção
    # ------------------------------------------------------------------
    def inserir(self, chave, valor: dict) -> bool:
        """
        Insere um novo cliente. Retorna False (sem alterar nada) se o ID já existir,
        pois o ID é único. Para alterar um registro existente, use `atualizar`.
        """
        chave = self._normalizar_chave(chave)

        if self.contem(chave):
            return False

        divisoes_antes = self.total_divisoes
        acessos = 1

        raiz = self.raiz
        if len(raiz.chaves) == self.max_chaves:
            # Raiz cheia: cria nova raiz e divide a antiga (a árvore cresce em altura)
            nova_raiz = self._novo_no(folha=False)
            nova_raiz.filhos.append(raiz)
            self.raiz = nova_raiz
            self._dividir_filho(nova_raiz, 0)
            acessos += 1

        acessos += self._inserir_em_no_nao_cheio(self.raiz, chave, valor)

        self.tamanho += 1
        self.ordem_insercao.append(chave)
        self.ultima_insercao = {
            "chave": chave,
            "acessos": acessos,
            "divisoes": self.total_divisoes - divisoes_antes,
        }
        return True

    def _dividir_filho(self, pai: NoB, indice: int):
        """
        Divide o filho cheio `pai.filhos[indice]` (2t - 1 chaves) em dois nós com
        t - 1 chaves cada; a chave mediana sobe para o pai.
        """
        t = self.t
        y = pai.filhos[indice]
        z = self._novo_no(folha=y.folha)

        chave_mediana = y.chaves[t - 1]
        valor_mediano = y.valores[t - 1]

        z.chaves = y.chaves[t:]
        z.valores = y.valores[t:]
        if not y.folha:
            z.filhos = y.filhos[t:]
            y.filhos = y.filhos[:t]

        y.chaves = y.chaves[:t - 1]
        y.valores = y.valores[:t - 1]

        pai.filhos.insert(indice + 1, z)
        pai.chaves.insert(indice, chave_mediana)
        pai.valores.insert(indice, valor_mediano)

        self.total_divisoes += 1
        self.historico_divisoes.append({
            "numero": self.total_divisoes,
            "no_dividido": y.id,
            "novo_no": z.id,
            "no_pai": pai.id,
            "chave_promovida": chave_mediana,
            "nova_raiz": pai is self.raiz and len(pai.chaves) == 1,
        })

    def _inserir_em_no_nao_cheio(self, no: NoB, chave: int, valor: dict) -> int:
        """Insere descendo a árvore; retorna a quantidade de nós adicionais visitados."""
        acessos = 0

        while True:
            i = len(no.chaves) - 1

            if no.folha:
                no.chaves.append(None)
                no.valores.append(None)
                while i >= 0 and chave < no.chaves[i]:
                    no.chaves[i + 1] = no.chaves[i]
                    no.valores[i + 1] = no.valores[i]
                    i -= 1
                no.chaves[i + 1] = chave
                no.valores[i + 1] = valor
                return acessos

            while i >= 0 and chave < no.chaves[i]:
                i -= 1
            i += 1

            if len(no.filhos[i].chaves) == self.max_chaves:
                self._dividir_filho(no, i)
                if chave > no.chaves[i]:
                    i += 1

            no = no.filhos[i]
            acessos += 1

    # ------------------------------------------------------------------
    # Alteração
    # ------------------------------------------------------------------
    def atualizar(self, chave, valor: dict) -> bool:
        """
        Substitui o registro associado a um ID existente (a chave não muda, então
        a estrutura da árvore permanece idêntica). Retorna False se o ID não existir.
        """
        chave = self._normalizar_chave(chave)
        no, i, _, _ = self._localizar(chave)
        if no is None:
            return False
        no.valores[i] = valor
        return True

    # ------------------------------------------------------------------
    # Percurso e listagem
    # ------------------------------------------------------------------
    def listar_todos(self) -> list:
        """Percurso em ordem: retorna todos os registros ordenados por ID."""
        resultado = []
        self._em_ordem(self.raiz, resultado)
        return resultado

    def _em_ordem(self, no: NoB, saida: list):
        for i in range(len(no.chaves)):
            if not no.folha:
                self._em_ordem(no.filhos[i], saida)
            saida.append(no.valores[i])
        if not no.folha:
            self._em_ordem(no.filhos[-1], saida)

    def listar_em_ordem_de_insercao(self) -> list:
        """
        Retorna os registros na ordem em que foram inseridos (utilizado na persistência).
        Cada registro é recuperado pela própria árvore, sem alterar a instrumentação.
        """
        resultado = []
        for chave in self.ordem_insercao:
            no, i, _, _ = self._localizar(chave)
            resultado.append(no.valores[i])
        return resultado

    def __len__(self) -> int:
        return self.tamanho

    # ------------------------------------------------------------------
    # Instrumentação
    # ------------------------------------------------------------------
    def altura(self) -> int:
        """Número de níveis da árvore (0 se vazia; 1 se só a raiz)."""
        if self.tamanho == 0:
            return 0
        niveis = 1
        no = self.raiz
        while not no.folha:
            no = no.filhos[0]
            niveis += 1
        return niveis

    def niveis(self) -> list:
        """
        Percurso em largura: lista de níveis, cada um com a lista de nós
        (id, chaves, folha). Utilizado na visualização da rota /arvore-b.
        """
        if self.tamanho == 0:
            return []

        niveis = []
        atual = [self.raiz]
        while atual:
            niveis.append([
                {"id": no.id, "chaves": list(no.chaves), "folha": no.folha}
                for no in atual
            ])
            proximo = []
            for no in atual:
                proximo.extend(no.filhos)
            atual = proximo
        return niveis

    def obter_metricas(self) -> dict:
        """
        Métricas de instrumentação para a rota /arvore-b:
        grau, ordem, altura, número de nós, ocupação, divisões e estatísticas de busca.
        """
        niveis = self.niveis()
        total_nos = sum(len(n) for n in niveis)
        nos_folha = len(niveis[-1]) if niveis else 0
        capacidade_total = total_nos * self.max_chaves
        ocupacao = round(100 * self.tamanho / capacidade_total, 1) if capacidade_total else 0.0

        media_acessos = (
            round(self.total_acessos_busca / self.total_buscas, 2) if self.total_buscas else 0.0
        )
        media_comparacoes = (
            round(self.total_comparacoes_busca / self.total_buscas, 2) if self.total_buscas else 0.0
        )

        return {
            "grau_minimo": self.t,
            "ordem": 2 * self.t,
            "min_chaves": self.min_chaves,
            "max_chaves": self.max_chaves,
            "tamanho": self.tamanho,
            "altura": self.altura(),
            "total_nos": total_nos,
            "nos_folha": nos_folha,
            "nos_internos": total_nos - nos_folha,
            "ocupacao": ocupacao,
            "total_divisoes": self.total_divisoes,
            "total_buscas": self.total_buscas,
            "media_acessos": media_acessos,
            "media_comparacoes": media_comparacoes,
            "ultima_busca": self.ultima_busca,
            "ultima_insercao": self.ultima_insercao,
            "historico_divisoes": list(reversed(self.historico_divisoes)),
        }

    # ------------------------------------------------------------------
    # Verificação das propriedades da Árvore B
    # ------------------------------------------------------------------
    def validar(self) -> tuple[bool, str]:
        """
        Confere as invariantes da Árvore B. Retorna (ok, mensagem).
        - chaves ordenadas dentro do nó e respeitando os limites impostos pelos pais;
        - ocupação entre t - 1 e 2t - 1 chaves (raiz exige apenas >= 1 se não vazia);
        - nó interno com k chaves possui k + 1 filhos;
        - todas as folhas no mesmo nível;
        - quantidade total de chaves coincide com `tamanho`.
        """
        profundidade_folhas = set()
        total = [0]
        erros = []

        def visitar(no, nivel, minimo, maximo):
            n = len(no.chaves)
            total[0] += n

            if no is not self.raiz and n < self.min_chaves:
                erros.append(f"nó {no.id} com {n} chaves (< {self.min_chaves})")
            if n > self.max_chaves:
                erros.append(f"nó {no.id} com {n} chaves (> {self.max_chaves})")
            if len(no.valores) != n:
                erros.append(f"nó {no.id} com chaves/valores dessincronizados")

            for i in range(n):
                if i > 0 and no.chaves[i - 1] >= no.chaves[i]:
                    erros.append(f"nó {no.id} com chaves fora de ordem")
                if minimo is not None and no.chaves[i] <= minimo:
                    erros.append(f"nó {no.id} viola limite inferior {minimo}")
                if maximo is not None and no.chaves[i] >= maximo:
                    erros.append(f"nó {no.id} viola limite superior {maximo}")

            if no.folha:
                profundidade_folhas.add(nivel)
                if no.filhos:
                    erros.append(f"folha {no.id} possui filhos")
                return

            if len(no.filhos) != n + 1:
                erros.append(f"nó {no.id} com {n} chaves e {len(no.filhos)} filhos")
                return

            for i, filho in enumerate(no.filhos):
                inferior = no.chaves[i - 1] if i > 0 else minimo
                superior = no.chaves[i] if i < n else maximo
                visitar(filho, nivel + 1, inferior, superior)

        visitar(self.raiz, 1, None, None)

        if len(profundidade_folhas) > 1:
            erros.append(f"folhas em níveis diferentes: {sorted(profundidade_folhas)}")
        if total[0] != self.tamanho:
            erros.append(f"contagem de chaves ({total[0]}) difere de tamanho ({self.tamanho})")
        if len(self.ordem_insercao) != self.tamanho:
            erros.append("ordem de inserção dessincronizada com a árvore")

        if erros:
            return False, "; ".join(erros[:3])
        return True, "Todas as propriedades da Árvore B estão satisfeitas."
