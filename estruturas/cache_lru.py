"""
DIFERENCIAL DA EQUIPE: Cache LRU (Least Recently Used) customizado com operações O(1).

Problema: o cálculo de rotas (Dijkstra) é repetido toda vez que clientes consultam os
mesmos destinos populares (ex: Brasil -> Itália). O cache guarda as rotas mais recentes
e descarta a MENOS recentemente usada quando fica cheio.

Como o O(1) é obtido (a mesma ideia de "chave -> nó" da Tabela Hash):
- Um índice hash (dicionário) leva da chave ao NÓ em O(1) médio.
- Uma lista duplamente encadeada, implementada aqui com nós próprios e dois sentinelas
  (cabeça e cauda), mantém a ordem de uso: logo após a cabeça fica o mais recente (MRU)
  e logo antes da cauda fica o menos recente (LRU).
- Como cada nó conhece seu anterior e seu próximo, mover um nó para a frente ou removê-lo
  é só religar 4 ponteiros, sem percorrer a lista. Por isso obter(), colocar(), remover()
  e o despejo do LRU custam O(1). (Uma lista comum custaria O(n) para achar/mover o nó.)

Operações que NÃO são O(1) por natureza: invalidar_se() e entradas() percorrem a lista
inteira (O(capacidade)), pois examinam todos os itens.

A classe não depende do Flask nem das demais estruturas: o chamador decide o que usar
como chave e valor.
"""

import time
from collections import deque


class NoLRU:
    """Nó da lista duplamente encadeada do cache."""
    __slots__ = ("chave", "valor", "anterior", "proximo", "criado_em", "acessos")

    def __init__(self, chave, valor, criado_em=0.0):
        self.chave = chave
        self.valor = valor
        self.anterior = None
        self.proximo = None
        self.criado_em = criado_em
        self.acessos = 0     # quantos HITs esta entrada já atendeu


class CacheLRU:
    """Cache LRU com capacidade fixa, TTL opcional e instrumentação completa."""

    def __init__(self, capacidade: int = 8, ttl_segundos: float | None = None,
                 relogio=time.monotonic, registrar_eventos: bool = True):
        if int(capacidade) < 1:
            raise ValueError("A capacidade do cache deve ser >= 1.")
        self.capacidade = int(capacidade)
        self.ttl_segundos = ttl_segundos if ttl_segundos else None
        self._relogio = relogio
        self._registrar = registrar_eventos

        # Sentinelas: evitam casos especiais ao inserir/remover nas pontas
        self._cabeca = NoLRU(None, None)   # cabeca.proximo = MRU
        self._cauda = NoLRU(None, None)    # cauda.anterior = LRU
        self._cabeca.proximo = self._cauda
        self._cauda.anterior = self._cabeca

        self._indice = {}                  # chave -> NoLRU (O(1))

        # Instrumentação
        self.hits = 0
        self.misses = 0
        self.insercoes = 0
        self.atualizacoes = 0
        self.evicoes = 0          # entradas descartadas por falta de espaço (política LRU)
        self.invalidacoes = 0     # entradas removidas porque a rede/países mudaram
        self.expiracoes = 0       # entradas removidas por TTL vencido
        self.eventos = deque(maxlen=30)
        self._sequencia = 0

    # ------------------------------------------------------------------
    # Lista encadeada (4 ponteiros por operação)
    # ------------------------------------------------------------------
    def _desligar(self, no: NoLRU):
        no.anterior.proximo = no.proximo
        no.proximo.anterior = no.anterior

    def _inserir_na_frente(self, no: NoLRU):
        no.anterior = self._cabeca
        no.proximo = self._cabeca.proximo
        self._cabeca.proximo.anterior = no
        self._cabeca.proximo = no

    def _expirado(self, no: NoLRU) -> bool:
        return self.ttl_segundos is not None and (self._relogio() - no.criado_em) > self.ttl_segundos

    def _evento(self, tipo: str, chave, detalhe: str = ""):
        if self._registrar:
            self._sequencia += 1
            self.eventos.appendleft({"n": self._sequencia, "tipo": tipo, "chave": chave, "detalhe": detalhe})

    # ------------------------------------------------------------------
    # Operações principais - O(1)
    # ------------------------------------------------------------------
    def obter(self, chave, padrao=None):
        """
        Devolve o valor associado à chave e o marca como o mais recentemente usado.
        Se a chave não existe (ou expirou), conta um MISS e devolve `padrao`.
        """
        no = self._indice.get(chave)
        if no is None:
            self.misses += 1
            self._evento("MISS", chave)
            return padrao
        if self._expirado(no):
            self._remover_no(no)
            self.expiracoes += 1
            self.misses += 1
            self._evento("EXPIROU", chave, "TTL vencido")
            return padrao

        self._desligar(no)
        self._inserir_na_frente(no)
        no.acessos += 1
        self.hits += 1
        self._evento("HIT", chave)
        return no.valor

    def colocar(self, chave, valor):
        """
        Insere (ou atualiza) a entrada como a mais recente. Se o cache está cheio,
        descarta a menos recentemente usada. Devolve a chave despejada ou None.
        """
        no = self._indice.get(chave)
        if no is not None:
            no.valor = valor
            no.criado_em = self._relogio()
            self._desligar(no)
            self._inserir_na_frente(no)
            self.atualizacoes += 1
            self._evento("ATUALIZA", chave)
            return None

        despejada = None
        if len(self._indice) >= self.capacidade:
            despejada = self._despejar_lru()

        no = NoLRU(chave, valor, self._relogio())
        self._indice[chave] = no
        self._inserir_na_frente(no)
        self.insercoes += 1
        self._evento("INSERE", chave)
        return despejada

    def _despejar_lru(self):
        """Remove o nó logo antes da cauda (o menos recentemente usado)."""
        no = self._cauda.anterior
        self._remover_no(no)
        self.evicoes += 1
        self._evento("DESPEJA", no.chave, "menos recentemente usada")
        return no.chave

    def _remover_no(self, no: NoLRU):
        self._desligar(no)
        del self._indice[no.chave]

    def remover(self, chave) -> bool:
        """Remove uma entrada específica (conta como invalidação)."""
        no = self._indice.get(chave)
        if no is None:
            return False
        self._remover_no(no)
        self.invalidacoes += 1
        self._evento("INVALIDA", chave)
        return True

    def espiar(self, chave, padrao=None):
        """Consulta sem alterar a ordem de uso nem os contadores."""
        no = self._indice.get(chave)
        return padrao if no is None else no.valor

    def __contains__(self, chave) -> bool:
        return chave in self._indice

    def __len__(self) -> int:
        return len(self._indice)

    # ------------------------------------------------------------------
    # Operações em lote - O(capacidade)
    # ------------------------------------------------------------------
    def invalidar_se(self, predicado) -> int:
        """Remove todas as entradas para as quais predicado(chave, valor) é verdadeiro."""
        removidas = 0
        no = self._cabeca.proximo
        while no is not self._cauda:
            proximo = no.proximo   # guarda antes de possivelmente desligar o nó
            if predicado(no.chave, no.valor):
                self._remover_no(no)
                self.invalidacoes += 1
                self._evento("INVALIDA", no.chave)
                removidas += 1
            no = proximo
        return removidas

    def limpar(self) -> int:
        """Esvazia o cache (conta cada entrada como invalidada). Mantém as estatísticas."""
        return self.invalidar_se(lambda chave, valor: True)

    def redimensionar(self, nova_capacidade: int) -> list:
        """Altera a capacidade; se diminuir, despeja as menos recentes. Devolve as chaves despejadas."""
        if int(nova_capacidade) < 1:
            raise ValueError("A capacidade do cache deve ser >= 1.")
        self.capacidade = int(nova_capacidade)
        despejadas = []
        while len(self._indice) > self.capacidade:
            despejadas.append(self._despejar_lru())
        return despejadas

    def configurar_ttl(self, ttl_segundos: float | None):
        self.ttl_segundos = ttl_segundos if ttl_segundos else None

    # ------------------------------------------------------------------
    # Instrumentação
    # ------------------------------------------------------------------
    def entradas(self) -> list:
        """Entradas da mais recente (MRU) para a menos recente (LRU)."""
        agora = self._relogio()
        saida, no, posicao = [], self._cabeca.proximo, 1
        while no is not self._cauda:
            idade = agora - no.criado_em
            saida.append({
                "posicao": posicao,
                "chave": no.chave,
                "valor": no.valor,
                "acessos": no.acessos,
                "idade_s": round(idade, 1),
                "expira_em_s": None if self.ttl_segundos is None else max(0, round(self.ttl_segundos - idade, 1)),
            })
            no, posicao = no.proximo, posicao + 1
        return saida

    def obter_metricas(self) -> dict:
        consultas = self.hits + self.misses
        return {
            "capacidade": self.capacidade,
            "tamanho": len(self._indice),
            "ocupacao": round(len(self._indice) / self.capacidade, 2),
            "ttl_segundos": self.ttl_segundos,
            "hits": self.hits,
            "misses": self.misses,
            "consultas": consultas,
            "taxa_acerto": round(100 * self.hits / consultas, 1) if consultas else 0.0,
            "insercoes": self.insercoes,
            "atualizacoes": self.atualizacoes,
            "evicoes": self.evicoes,
            "invalidacoes": self.invalidacoes,
            "expiracoes": self.expiracoes,
            "eventos": list(self.eventos),
        }

    def validar(self) -> tuple[bool, str]:
        """Confere a consistência: índice e lista encadeada devem conter as mesmas chaves."""
        vistas, no, anterior = [], self._cabeca.proximo, self._cabeca
        while no is not self._cauda:
            if no.anterior is not anterior:
                return False, "Ponteiro 'anterior' inconsistente."
            vistas.append(no.chave)
            anterior, no = no, no.proximo
            if len(vistas) > len(self._indice):
                return False, "A lista encadeada tem mais nós que o índice."
        if self._cauda.anterior is not anterior:
            return False, "A cauda não aponta para o último nó."
        if len(vistas) != len(self._indice) or set(vistas) != set(self._indice):
            return False, "Índice e lista encadeada divergem."
        if len(vistas) > self.capacidade:
            return False, "O cache excede a capacidade."
        return True, "Índice e lista encadeada consistentes."
