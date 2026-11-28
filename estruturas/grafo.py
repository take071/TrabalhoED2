"""
Objetivo:
Implementar o Grafo ponderado e não-direcionado que representa a rede internacional
da GlobalSIM. Cada país atendido é um vértice (identificado pelo código de duas letras)
e cada aresta é uma conexão da infraestrutura cujo peso é a latência simulada em ms.

Representação: lista de adjacência. Para cada vértice guardamos os vizinhos e o peso da
aresta (um dicionário interno, o que permite consultar/atualizar/remover uma aresta em
O(1) médio). Como o grafo é não-direcionado, cada aresta é gravada nas duas listas.

Algoritmos implementados (todos instrumentados, para a tela de rede e a apresentação):
- BFS (busca em largura): fila FIFO; devolve ordem de visita, nível e pai de cada vértice.
  Gera o menor caminho em NÚMERO DE SALTOS (ignora as latências).
- DFS (busca em profundidade): pilha explícita (sem recursão); devolve ordem de visita,
  profundidade, pai e os tempos de descoberta/finalização de cada vértice.
- Dijkstra: menor caminho em SOMA DE LATÊNCIAS, usando uma fila de prioridade (min-heap
  binário) implementada neste arquivo. Requer pesos positivos.

Os vizinhos são sempre percorridos em ordem alfabética para que a execução seja
determinística (mesma saída em toda execução, o que facilita testes e demonstração).
"""

import time
from collections import deque

INFINITO = float("inf")


class FilaPrioridade:
    """
    Min-heap binário (vetor) usado pelo Dijkstra.
    Cada elemento é uma tupla (prioridade, item); empates são desfeitos pelo item.
    inserir() e remover_minimo() custam O(log n).
    """

    def __init__(self):
        self._heap = []

    def __len__(self):
        return len(self._heap)

    def inserir(self, prioridade, item):
        self._heap.append((prioridade, item))
        self._subir(len(self._heap) - 1)

    def remover_minimo(self):
        heap = self._heap
        topo = heap[0]
        ultimo = heap.pop()
        if heap:
            heap[0] = ultimo
            self._descer(0)
        return topo

    def _subir(self, i):
        heap = self._heap
        while i > 0:
            pai = (i - 1) // 2
            if heap[i] < heap[pai]:
                heap[i], heap[pai] = heap[pai], heap[i]
                i = pai
            else:
                break

    def _descer(self, i):
        heap = self._heap
        n = len(heap)
        while True:
            esq, dir_ = 2 * i + 1, 2 * i + 2
            menor = i
            if esq < n and heap[esq] < heap[menor]:
                menor = esq
            if dir_ < n and heap[dir_] < heap[menor]:
                menor = dir_
            if menor == i:
                break
            heap[i], heap[menor] = heap[menor], heap[i]
            i = menor


def _numero(valor):
    """Mostra latências inteiras sem '.0' (ex: 80.0 -> 80)."""
    return int(valor) if float(valor).is_integer() else valor


class Grafo:
    """Grafo ponderado não-direcionado com BFS, DFS e Dijkstra instrumentados."""

    def __init__(self):
        self._adj = {}   # vértice -> {vizinho: latência}

    # ------------------------------------------------------------------
    # Vértices
    # ------------------------------------------------------------------
    @staticmethod
    def _normalizar(vertice) -> str:
        return str(vertice).strip().upper()

    def adicionar_vertice(self, vertice) -> bool:
        """Adiciona o vértice; devolve False se ele já existia."""
        v = self._normalizar(vertice)
        if not v or v in self._adj:
            return False
        self._adj[v] = {}
        return True

    def remover_vertice(self, vertice) -> bool:
        """Remove o vértice e todas as arestas incidentes a ele."""
        v = self._normalizar(vertice)
        if v not in self._adj:
            return False
        for vizinho in self._adj[v]:
            del self._adj[vizinho][v]
        del self._adj[v]
        return True

    def tem_vertice(self, vertice) -> bool:
        return self._normalizar(vertice) in self._adj

    def vertices(self) -> list:
        return sorted(self._adj)

    # ------------------------------------------------------------------
    # Arestas
    # ------------------------------------------------------------------
    def adicionar_aresta(self, origem, destino, latencia) -> str:
        """
        Cria a aresta (ou atualiza a latência se já existir).
        Devolve 'criada' ou 'atualizada'. Levanta ValueError para vértices inexistentes,
        laço (origem == destino) ou latência não positiva.
        """
        u, v = self._normalizar(origem), self._normalizar(destino)
        if u not in self._adj or v not in self._adj:
            raise ValueError("Os dois países precisam existir no grafo.")
        if u == v:
            raise ValueError("Não é permitido ligar um país a ele mesmo.")
        try:
            peso = float(latencia)
        except (TypeError, ValueError):
            raise ValueError("A latência deve ser um número.")
        if peso != peso or peso <= 0 or peso == INFINITO:
            raise ValueError("A latência deve ser um número positivo (o Dijkstra exige pesos > 0).")
        peso = _numero(peso)

        existia = v in self._adj[u]
        self._adj[u][v] = peso
        self._adj[v][u] = peso
        return "atualizada" if existia else "criada"

    def remover_aresta(self, origem, destino) -> bool:
        u, v = self._normalizar(origem), self._normalizar(destino)
        if u not in self._adj or v not in self._adj[u]:
            return False
        del self._adj[u][v]
        del self._adj[v][u]
        return True

    def tem_aresta(self, origem, destino) -> bool:
        u, v = self._normalizar(origem), self._normalizar(destino)
        return u in self._adj and v in self._adj[u]

    def peso(self, origem, destino):
        u, v = self._normalizar(origem), self._normalizar(destino)
        return self._adj.get(u, {}).get(v)

    def vizinhos(self, vertice) -> list:
        """Lista [(vizinho, latência)] em ordem alfabética."""
        v = self._normalizar(vertice)
        return sorted(self._adj.get(v, {}).items())

    def arestas(self) -> list:
        """Lista cada aresta uma única vez: [(u, v, latência)] com u < v."""
        saida = []
        for u in sorted(self._adj):
            for v, peso in sorted(self._adj[u].items()):
                if u < v:
                    saida.append((u, v, peso))
        return saida

    def lista_adjacencia(self) -> list:
        """Representação textual da lista de adjacência, para exibição."""
        return [
            {"vertice": u, "grau": len(self._adj[u]),
             "vizinhos": [{"vertice": v, "latencia": p} for v, p in sorted(self._adj[u].items())]}
            for u in sorted(self._adj)
        ]

    def __len__(self):
        return len(self._adj)

    def _exigir(self, vertice) -> str:
        v = self._normalizar(vertice)
        if v not in self._adj:
            raise ValueError(f"Vértice '{v}' não existe no grafo.")
        return v

    # ------------------------------------------------------------------
    # BFS - busca em largura
    # ------------------------------------------------------------------
    def bfs(self, origem) -> dict:
        """
        Percorre o grafo por camadas a partir da origem usando uma fila FIFO.
        Complexidade O(V + E). Os níveis informam o menor número de saltos.
        """
        origem = self._exigir(origem)
        inicio = time.perf_counter_ns()

        fila = deque([origem])
        nivel = {origem: 0}
        pai = {origem: None}
        ordem = []
        examinadas = 0

        while fila:
            u = fila.popleft()
            ordem.append(u)
            for v, _ in sorted(self._adj[u].items()):
                examinadas += 1
                if v not in nivel:
                    nivel[v] = nivel[u] + 1
                    pai[v] = u
                    fila.append(v)

        por_nivel = []
        for v in ordem:
            while len(por_nivel) <= nivel[v]:
                por_nivel.append([])
            por_nivel[nivel[v]].append(v)

        return {
            "algoritmo": "BFS",
            "origem": origem,
            "ordem": ordem,
            "niveis": nivel,
            "por_nivel": por_nivel,
            "pai": pai,
            "alcancados": len(ordem),
            "nao_alcancados": [v for v in sorted(self._adj) if v not in nivel],
            "arestas_examinadas": examinadas,
            "tempo_ns": time.perf_counter_ns() - inicio,
        }

    def caminho_menos_saltos(self, origem, destino) -> list | None:
        """Menor caminho em número de saltos (via BFS), ou None se não houver."""
        destino = self._exigir(destino)
        resultado = self.bfs(origem)
        if destino not in resultado["pai"]:
            return None
        caminho, atual = [], destino
        while atual is not None:
            caminho.append(atual)
            atual = resultado["pai"][atual]
        return caminho[::-1]

    # ------------------------------------------------------------------
    # DFS - busca em profundidade
    # ------------------------------------------------------------------
    def dfs(self, origem) -> dict:
        """
        Percorre o grafo em profundidade com uma pilha explícita (iterativa), na mesma
        ordem que a versão recursiva. Registra descoberta/finalização de cada vértice.
        Complexidade O(V + E).
        """
        origem = self._exigir(origem)
        inicio = time.perf_counter_ns()

        descoberta = {origem: 1}
        finalizacao = {}
        profundidade = {origem: 0}
        pai = {origem: None}
        ordem = [origem]
        examinadas = 0
        # Cada item da pilha guarda o vértice e o iterador dos seus vizinhos ainda não vistos
        pilha = [(origem, iter(sorted(self._adj[origem])))]
        relogio = 1

        while pilha:
            u, vizinhos = pilha[-1]
            avancou = False
            for v in vizinhos:
                examinadas += 1
                if v not in descoberta:
                    relogio += 1
                    descoberta[v] = relogio
                    profundidade[v] = profundidade[u] + 1
                    pai[v] = u
                    ordem.append(v)
                    pilha.append((v, iter(sorted(self._adj[v]))))
                    avancou = True
                    break
            if not avancou:
                relogio += 1
                finalizacao[u] = relogio
                pilha.pop()

        return {
            "algoritmo": "DFS",
            "origem": origem,
            "ordem": ordem,
            "profundidade": profundidade,
            "profundidade_maxima": max(profundidade.values()),
            "pai": pai,
            "descoberta": descoberta,
            "finalizacao": finalizacao,
            "alcancados": len(ordem),
            "nao_alcancados": [v for v in sorted(self._adj) if v not in descoberta],
            "arestas_examinadas": examinadas,
            "tempo_ns": time.perf_counter_ns() - inicio,
        }

    # ------------------------------------------------------------------
    # Dijkstra - menor caminho por soma de latências
    # ------------------------------------------------------------------
    def dijkstra(self, origem, destino=None) -> dict:
        """
        Menor latência acumulada a partir da origem (pesos positivos).
        - Com destino: o algoritmo para assim que o destino é finalizado.
        - Sem destino: calcula a distância até todos os vértices alcançáveis.
        Usa uma fila de prioridade com remoção preguiçosa (entradas obsoletas são
        ignoradas ao sair da fila). Complexidade O((V + E) log V).
        """
        origem = self._exigir(origem)
        if destino is not None:
            destino = self._exigir(destino)
        inicio = time.perf_counter_ns()

        distancia = {v: INFINITO for v in self._adj}
        distancia[origem] = 0
        anterior = {}
        fila = FilaPrioridade()
        fila.inserir(0, origem)

        finalizados = set()
        ordem_expansao = []
        relaxamentos = 0
        examinadas = 0

        while len(fila):
            d, u = fila.remover_minimo()
            if u in finalizados:
                continue  # entrada obsoleta: já existe um caminho melhor finalizado
            finalizados.add(u)
            ordem_expansao.append({"vertice": u, "distancia": _numero(d)})
            if destino is not None and u == destino:
                break
            for v, peso in sorted(self._adj[u].items()):
                examinadas += 1
                if v in finalizados:
                    continue
                nova = d + peso
                if nova < distancia[v]:
                    distancia[v] = nova
                    anterior[v] = u
                    relaxamentos += 1
                    fila.inserir(nova, v)

        encontrada, caminho, latencia = False, [], None
        if destino is not None and distancia[destino] != INFINITO:
            encontrada = True
            atual = destino
            while True:
                caminho.append(atual)
                if atual == origem:
                    break
                atual = anterior[atual]
            caminho.reverse()
            latencia = _numero(distancia[destino])

        return {
            "algoritmo": "Dijkstra",
            "origem": origem,
            "destino": destino,
            "encontrada": encontrada,
            "caminho": caminho,
            "latencia": latencia,
            "distancias": {v: (None if d == INFINITO else _numero(d)) for v, d in distancia.items()},
            "ordem_expansao": ordem_expansao,
            "nos_expandidos": len(ordem_expansao),
            "relaxamentos": relaxamentos,
            "arestas_examinadas": examinadas,
            "tempo_ns": time.perf_counter_ns() - inicio,
        }

    def latencia_do_caminho(self, caminho) -> float | int | None:
        """Soma as latências ao longo de um caminho (None se alguma aresta não existir)."""
        total = 0
        for u, v in zip(caminho, caminho[1:]):
            peso = self.peso(u, v)
            if peso is None:
                return None
            total += peso
        return _numero(total)

    # ------------------------------------------------------------------
    # Métricas
    # ------------------------------------------------------------------
    def componentes_conexos(self) -> list:
        """Lista de componentes conexos (cada um é uma lista ordenada de vértices)."""
        vistos, componentes = set(), []
        for v in sorted(self._adj):
            if v not in vistos:
                alcancados = self.bfs(v)["ordem"]
                vistos.update(alcancados)
                componentes.append(sorted(alcancados))
        return componentes

    def obter_metricas(self) -> dict:
        n = len(self._adj)
        m = len(self.arestas())
        graus = {v: len(self._adj[v]) for v in sorted(self._adj)}
        componentes = self.componentes_conexos()
        return {
            "vertices": n,
            "arestas": m,
            "graus": graus,
            "grau_maximo": max(graus.values()) if graus else 0,
            "densidade": round(2 * m / (n * (n - 1)), 3) if n > 1 else 0.0,
            "componentes": componentes,
            "conexo": len(componentes) <= 1,
        }

    def para_dict(self) -> dict:
        """Formato gravado em arquivos/rede.json (os vértices vêm da Tabela Hash)."""
        return {
            "arestas": [
                {"origem": u, "destino": v, "latencia": peso}
                for u, v, peso in self.arestas()
            ]
        }
