"""
Módulo de Estruturas de Dados do GlobalSIM (ED2)

Etapa 1:
- Tabela Hash (tabela_hash.py): Armazenamento e consulta dos países atendidos.

Etapa 2:
- Árvore B (arvore_b.py): Indexação e gerenciamento de clientes e eSIMs por ID.
"""

from estruturas.tabela_hash import NoHash, TabelaHash
from estruturas.arvore_b import NoB, ArvoreB

__all__ = ["NoHash", "TabelaHash", "NoB", "ArvoreB"]
