<h1 align="center">GlobalSIM - Serviço Internacional de Internet por eSIM</h1>

<p align="center">
  <img src="static/img/logo.png" alt="GlobalSIM Logo" width="480">
</p>

<p align="center">
  <strong>Universidade do Estado da Bahia (UNEB)</strong><br>
  Departamento de Ciências Exatas e da Terra - Campus I<br>
  Colegiado de Sistemas de Informação<br>
  Disciplina: Estruturas de Dados II<br>
  Docente: Profa. Maria Inés Restovic
</p>

### Equipe
- Arthur Felipe
- Lucas Vinicius
- Raphael Lopes

---

## 1. Descrição do Projeto

O projeto consiste no desenvolvimento incremental de uma aplicação Web em Python com Flask para administrar os serviços da **GlobalSIM**, uma empresa fictícia de Internet móvel internacional via eSIM.

O principal objetivo do trabalho é aplicar, analisar e integrar as estruturas de dados estudadas na disciplina em um cenário prático de roteamento e telecomunicações:

- **Etapa 1 (Tabela Hash — Concluída):** Cadastro, gerenciamento e consulta de cobertura dos países atendidos em $O(1)$ médio, com mapas interativos Folium e validação geográfica via Geopy.
- **Etapa 2 (Árvore B — Concluída):** Gerenciamento e indexação de ~1.000 clientes e eSIMs em $O(\log n)$, consulta integrada Cliente × País de Destino e instrumentação visual da Árvore B.
- **Etapa 3 (Grafos + Diferencial Cache LRU — Próxima etapa):** Modelagem da rede internacional com BFS, DFS e Dijkstra (rotas de menor latência) otimizadas por um **Sistema de Cache LRU Customizado** em $O(1)$.

A persistência dos dados é realizada em arquivos JSON, carregados nas estruturas em memória durante a inicialização da aplicação, mantendo a lógica das estruturas de dados estritamente separada das rotas e controladores do Flask.

> 📋 **Acompanhamento das Etapas e Diferencial:** Consulte os roadmaps detalhados na pasta [`etapas/`](etapas/):
> - [Roadmap & Checklist da Etapa 1 (Tabela Hash)](etapas/ETAPA_1_TODOS.md)
> - [Roadmap & Checklist da Etapa 2 (Árvore B)](etapas/ETAPA_2_TODOS.md)
> - [Roadmap & Checklist da Etapa 3 (Grafos & Integração Final)](etapas/ETAPA_3_TODOS.md)
> - [Especificação do Diferencial — Sistema de Cache LRU Customizado](etapas/DIFERENCIAL_CACHE_LRU.md)

---

## 2. Diferencial da Equipe

**Tema:** Sistema de Cache LRU (*Least Recently Used*) Customizado para Otimização de Rotas.

### Problema abordado
Na integração final da Etapa 3, o cálculo da rota de menor latência via algoritmo de Dijkstra possui complexidade $O((V + E)\log V)$, o que se torna custoso em redes maiores quando diversos clientes consultam repetidamente pares populares de origem e destino (como `BR → IT`, `BR → US` ou `PT → FR`).

### Solução e integração às estruturas do projeto
Em vez de recorrer a bibliotecas prontas de cache do Python (como `functools.lru_cache` ou `collections.OrderedDict`), o sistema implementa artesanalmente uma **estrutura híbrida** que otimiza a Etapa 3 e se conecta diretamente às mutações da Etapa 1:

1. **Lista/Fila Duplamente Encadeada + Tabela Hash Própria ($O(1)$):**
   - Cada entrada armazenada no cache é um nó (`NoLRU`) em uma lista duplamente encadeada com sentinelas (`HEAD` = mais recente / MRU; `TAIL` = menos recente / LRU).
   - A própria **`TabelaHash`** implementada na Etapa 1 (`estruturas/tabela_hash.py`) indexa a chave da rota (ex.: `"BR->IT"`) diretamente para a referência do `NoLRU`, permitindo **Cache Hit**, promoção para MRU e descarte (*eviction*) do LRU em tempo **$O(1)$ médio**.
2. **Integração com Dijkstra (Etapa 3):**
   - Antes de executar o Dijkstra no grafo, o sistema consulta o Cache LRU. Em caso de **Hit**, retorna imediatamente a rota e a latência em $O(1)$ sem percorrer o grafo; em caso de **Miss**, calcula via Dijkstra e armazena o resultado no topo do cache.
3. **Lógica de Expiração e Consistência (Etapa 1 e Etapa 3):**
   - Sempre que a rede ou a base de países sofrer alteração (cadastro, edição ou remoção de país nas rotas da Etapa 1, ou alteração de conexões/latências na Etapa 3), o cache é automaticamente **invalidado** para impedir o retorno de rotas desatualizadas ou inconsistentes.

Para detalhes arquiteturais, diagramas, contrato das classes e plano de testes, consulte [`etapas/DIFERENCIAL_CACHE_LRU.md`](etapas/DIFERENCIAL_CACHE_LRU.md).

---

## 3. Estrutura de Diretórios do Projeto

```text
Trabalho-ED2/
├── app.py                     # Aplicação Web Flask principal e rotas (Etapas 1 e 2)
├── requirements.txt           # Dependências Python (Flask, Folium, Geopy)
├── shell.nix                  # Configuração de ambiente reprodutível (Nix/NixOS)
├── README.md                  # Documentação e relatório principal do projeto
├── .gitignore                 # Arquivos ignorados pelo controle de versão
│
├── estruturas/                # Núcleo das Estruturas de Dados (ED2)
│   ├── __init__.py
│   ├── tabela_hash.py         # [Etapa 1] Tabela Hash própria com encadeamento separado
│   └── arvore_b.py            # [Etapa 2] Árvore B própria (grau t=3, split preventivo, validação)
│
├── arquivos/                  # Persistência em disco (JSON)
│   ├── paises.json            # [Etapa 1] Base dos países atendidos e coordenadas (lat/lon)
│   ├── clientes.json          # [Etapa 2] Massa de ~1.000 clientes e eSIMs
│   └── pacotes.json           # [Etapa 2] Catálogo oficial de pacotes de serviço
│
├── templates/                 # Camada de apresentação (Jinja2 + Bootstrap 5)
│   ├── base.html              # Layout base com navegação integrada e rodapé acadêmico
│   ├── index.html             # Dashboard principal com mapa Folium e resumo das estruturas
│   ├── cobertura.html         # Consulta em tempo O(1) com mapa do destino
│   ├── paises.html            # Gestão gerencial (CRUD) de destinos
│   ├── clientes.html          # Gestão paginada, busca por ID e associação de eSIM/pacote
│   ├── consulta.html          # Consulta integrada Cliente (Árvore B) x Destino (Tabela Hash)
│   ├── instrumentacao.html    # Inspeção visual dos 17 buckets da Tabela Hash
│   ├── arvore_b.html          # Inspeção visual por níveis, splits e caminho de busca da Árvore B
│   └── design_system.html     # Catálogo de componentes visuais
│
├── static/                    # Arquivos estáticos servidos pelo Flask
│   ├── css/
│   │   └── style.css          # Design system e estilos das Etapas 1 e 2
│   ├── js/
│   └── img/
│       ├── logo.png
│       └── globe-routes.png
│
├── etapas/                    # Roadmaps, backlogs e especificação do diferencial
│   ├── ETAPA_1_TODOS.md
│   ├── ETAPA_2_TODOS.md
│   ├── ETAPA_3_TODOS.md
│   └── DIFERENCIAL_CACHE_LRU.md
│
├── tests/                     # Testes automatizados (unittest)
│   ├── __init__.py
│   ├── test_tabela_hash.py    # Testes unitários da Tabela Hash
│   ├── test_arvore_b.py       # Testes unitários da Árvore B (invariantes, splits, 1.000 registros)
│   └── test_app.py            # Testes de integração das rotas Flask (Etapas 1 e 2)
│
├── docs/                      # Materiais acadêmicos e referências da disciplina
│   ├── AULAS-ED-2.pdf
│   └── TrabalhoPratico-2026.2.pdf
│
└── scripts/                   # Scripts utilitários
    ├── gerar_clientes.py      # Gerador determinístico de ~1.000 clientes (arquivos/clientes.json)
    └── gerar_mapa_demo.py     # Script auxiliar de teste do mapa Folium
```

---

## 4. Instruções de Execução

### Pré-requisitos
- Python 3.10 ou superior
- Gerenciador de pacotes `pip` (ou Nix/NixOS)

### Opção A: Execução no Nix / NixOS (Ambiente Reprodutível)

O repositório inclui `shell.nix` configurado com Python 3 e todas as dependências (`flask`, `folium`, `geopy`):

```bash
nix-shell --run "python3 app.py"
```

### Opção B: Execução com Ambiente Virtual Padrão (`venv`)

```bash
# Linux / macOS:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

```powershell
# Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

A aplicação ficará disponível em: **`http://localhost:5000`**

---

## 5. Testes Automatizados

Execute toda a suíte de testes (Tabela Hash, Árvore B e rotas Flask):

```bash
# Via Python padrão / venv:
python3 -m unittest discover -s tests -v

# Ou via NixOS:
nix-shell --run "python3 -m unittest discover -s tests -v"
```
