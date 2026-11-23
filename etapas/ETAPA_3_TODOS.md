# 🕸️ GlobalSIM — Roadmap & Backlog (Etapa 3)

> **Instituição:** Universidade do Estado da Bahia (UNEB) — Campus I  
> **Disciplina:** Estruturas de Dados II  
> **Docente:** Profa. Maria Inés Restovic  
> **Equipe:** Arthur Felipe, Lucas Vinicius, Raphael Lopes  

---

## Escopo da Etapa 3: Grafos, Integração Final e Cache LRU Customizado

- [ ] Modelagem da topologia de rede internacional ponderada (latências em ms) em `estruturas/grafo.py` com persistência em `arquivos/rede.json`.
- [ ] Implementação de algoritmos de percurso e roteamento: **BFS**, **DFS** e **Dijkstra** (rota de menor latência).
- [ ] Implementação do **Diferencial da Equipe — Sistema de Cache LRU Customizado** em `estruturas/cache_lru.py` (Fila Duplamente Encadeada + Tabela Hash própria em $O(1)$, com invalidação automática ao alterar países da Etapa 1 ou arestas do grafo).
  - 📋 Especificação técnica completa em [`etapas/DIFERENCIAL_CACHE_LRU.md`](DIFERENCIAL_CACHE_LRU.md).
- [ ] Consulta final integrada reunindo as 4 estruturas: **Árvore B** (cliente) × **Tabela Hash** (cobertura) × **Cache LRU** (atalho $O(1)$ de rotas) × **Grafo/Dijkstra** (cálculo de menor latência).
- [ ] Visualização interativa do Grafo (`/rede`) e painel de instrumentação do Cache LRU (`/cache-lru`).
- [ ] Bateria completa de testes unitários e de integração (`tests/test_grafo.py`, `tests/test_cache_lru.py`, `tests/test_app.py`).
