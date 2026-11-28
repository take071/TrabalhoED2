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

- **Etapa 1 (Tabela Hash):** Cadastro, gerenciamento e consulta de cobertura dos países atendidos.
- **Etapa 2 (Árvore B):** Gerenciamento e indexação de um grande volume de clientes e eSIMs (~1.000 registros).
- **Etapa 3 (Grafos):** Modelagem da rede internacional com cálculo de rotas de menor latência (BFS, DFS e Dijkstra) e consulta integrada cliente × cobertura × rede.
- **Diferencial:** Cache LRU customizado em O(1) para as rotas calculadas.

A persistência dos dados é realizada em arquivos JSON, carregados nas estruturas em memória durante a inicialização da aplicação, mantendo a lógica das estruturas de dados estritamente separada das rotas e controladores do Flask.

> 📋 **Acompanhamento da Etapa 1:** Consulte o [Roadmap & Checklist da Etapa 1](ETAPA_1_TODOS.md) para acompanhar o progresso detalhado, arquitetura e critérios de aceite das entregas.

---

## 2. Diferencial da Equipe

**Tema:** Sistema de Cache LRU (Least Recently Used) Customizado em O(1) para Consultas de Rotas.
**Código:** [`estruturas/cache_lru.py`](estruturas/cache_lru.py) (a estrutura) e [`estruturas/servico_rotas.py`](estruturas/servico_rotas.py) (integração com o Grafo e benchmark). **Tela:** `/cache`.

### Problema abordado
O cálculo da rota de menor latência (Dijkstra) é repetido toda vez que clientes consultam os mesmos destinos populares (ex: Brasil → Itália). Sem memória temporária, o sistema refaz a mesma travessia do grafo a cada consulta.

### Estrutura e algoritmo
- **Índice hash** (dicionário interno): leva a chave `ORIGEM->DESTINO` ao nó correspondente em O(1) médio.
- **Lista duplamente encadeada própria** (`NoLRU`, com nós sentinelas de cabeça e cauda): mantém a ordem de uso. Logo após a cabeça fica o mais recente (MRU); logo antes da cauda, o menos recente (LRU).
- **`obter` (HIT):** acha o nó pelo índice e o move para a frente religando 4 ponteiros. **`colocar` (MISS):** insere na frente; se estiver cheio, remove o nó anterior à cauda. Todas essas operações são **O(1)**, sem percorrer a lista.
- **Extras:** TTL opcional (expiração preguiçosa), redimensionamento em tempo de execução, `validar()` (confere a consistência entre índice e lista) e instrumentação (hits, misses, taxa de acerto, despejos, invalidações, expirações e log dos últimos eventos).
- `invalidar_se()`, `limpar()` e `entradas()` percorrem a lista e custam O(capacidade); isso é inevitável, pois examinam todos os itens.

### Como se integra às três estruturas
1. **Grafo (fonte da verdade):** o Dijkstra só roda em caso de *cache miss*. O resultado (caminho, latência e estatísticas) é gravado no cache, e as próximas consultas idênticas são respondidas sem nova travessia. Rotas inexistentes também são guardadas.
2. **Tabela Hash:** a mesma ideia chave → valor sustenta o índice do cache, e as alterações nos países funcionam como gatilhos: **remover um país** invalida somente as rotas em que ele é origem, destino ou escala (e o vértice sai do grafo); **cadastrar** um país cria um vértice isolado. Editar dados descritivos (operadora, tecnologia etc.) não invalida o cache, porque a rota depende apenas dos códigos dos países e das latências, e não dessas informações.
3. **Árvore B e consulta integrada:** a consulta final busca o cliente na Árvore B, verifica o destino na Tabela Hash e obtém a rota pelo cache (HIT/MISS aparece na tela).
4. **Mudança na rede:** criar, alterar ou remover uma conexão invalida **todo** o cache (qualquer rota pode ter mudado).

### Evidências para a apresentação
Em `/cache` o botão **Benchmark** compara "sempre Dijkstra" com caches de capacidades 1 a 64 sobre a mesma carga de consultas (destinos populares, semente fixa) e mede o custo por operação do cache com capacidades de 100 a 100.000 (deve permanecer praticamente constante, evidência do O(1)). A medida mais confiável é a **redução de nós expandidos** (determinística); o tempo depende da máquina e, como o grafo tem só 8 vértices, o Dijkstra já é muito rápido: com caches minúsculos o ganho de tempo pode ser nulo. O ganho aparece quando a capacidade cobre os pares mais consultados.

---

## 3. Estrutura de Diretórios (Etapas 1, 2 e 3)

O projeto é construído de forma incremental. Cada etapa foi adicionada preservando integralmente as anteriores:

```text
Trabalho-ED2/
├── app.py                     # Aplicação Flask: rotas das Etapas 1, 2 e 3, carga e persistência
├── gerar_clientes.py          # [Etapa 2] Gerador automático de clientes (clientes.json)
├── shell.nix                  # (Opcional) Configuração de ambiente para Nix/NixOS
├── requirements.txt           # Dependências do projeto (Flask)
├── README.md                  # Documentação e relatório do projeto
│
├── estruturas/                # Implementação das estruturas de dados (sem Flask)
│   ├── __init__.py
│   ├── tabela_hash.py         # [Etapa 1] Tabela Hash própria com instrumentação
│   ├── arvore_b.py            # [Etapa 2] Árvore B própria com instrumentação
│   ├── grafo.py               # [Etapa 3] Grafo ponderado: BFS, DFS e Dijkstra (com min-heap próprio)
│   ├── cache_lru.py           # [Diferencial] Cache LRU customizado em O(1)
│   └── servico_rotas.py       # [Diferencial] Integração Grafo + Cache, invalidação e benchmark
│
├── arquivos/                  # Persistência em disco (JSON)
│   ├── paises.json            # [Etapa 1] Países atendidos
│   ├── clientes.json          # [Etapa 2] ~1.000 clientes e eSIMs
│   ├── pacotes.json           # [Etapa 2] Pacotes de serviço (101, 102, 201, 202, 301)
│   └── rede.json              # [Etapa 3] Arestas da rede (latências em ms)
│
├── templates/                 # Templates Jinja2 (Bootstrap 5)
│   ├── base.html, index.html
│   ├── cobertura.html, paises.html, instrumentacao.html    # [Etapa 1]
│   ├── clientes.html, consulta.html, arvore_b.html         # [Etapa 2]
│   └── rede.html, cache.html                               # [Etapa 3] e diferencial
│
├── tests/
│   ├── test_arvore_b.py       # [Etapa 2] Testes unitários da Árvore B
│   ├── test_grafo.py          # [Etapa 3] Testes do Grafo, BFS, DFS e Dijkstra
│   ├── test_cache_lru.py      # [Diferencial] Testes do Cache LRU, do serviço e do benchmark
│   └── test_integracao_web.py # [Etapa 3] Testes das rotas Flask (usa cópia temporária dos JSONs)
│
└── static/                    # CSS, imagens e JS
```

---

## 3.1 Etapa 2: Árvore B e Gerenciamento de Clientes

### Árvore B (`estruturas/arvore_b.py`)
- **Chave:** ID único do cliente (inteiro). **Valor:** registro completo (`id`, `nome`, `email`, `esim`, `pacote`, `status`).
- **Grau mínimo `t = 3`:** cada nó tem de 2 a 5 chaves (a raiz pode ter menos) e até 6 filhos. O grau é um parâmetro do construtor (`ArvoreB(grau_minimo=...)`).
- **Inserção com divisão preventiva:** durante a descida, qualquer nó cheio (`2t - 1` chaves) é dividido em dois e a mediana sobe ao pai. Quando a raiz se divide, a altura cresce em 1.
- **Busca:** desce a partir da raiz comparando as chaves de cada nó; devolve também o caminho percorrido, o número de nós visitados e de comparações.
- **Alteração:** `atualizar(id, registro)` troca o registro sem mudar a forma da árvore.
- **Listagem:** percurso em ordem, que devolve os clientes ordenados por ID.
- **Instrumentação:** altura, total de nós (internos/folhas), ocupação média, total de divisões, histórico das últimas divisões, estatísticas de busca e verificação automática das propriedades da Árvore B (`validar()`).
- **Regra da disciplina:** listas Python existem apenas *dentro* de cada nó; a navegação, a busca e as divisões são feitas pela própria árvore. A busca de cliente nunca é feita sobre uma lista carregada do JSON.
- **Não implementado:** remoção de clientes, que não é exigida no enunciado da Etapa 2.

### Persistência
Os clientes são carregados de `arquivos/clientes.json` para a Árvore B na inicialização e gravados de volta (escrita atômica) a cada cadastro, alteração ou associação. A gravação segue a **ordem de inserção**: como a inserção é determinística, reiniciar o servidor reconstrói exatamente a mesma árvore (mesma altura, mesmos nós, mesmas divisões), o que mantém a instrumentação estável.

### Rotas da Etapa 2
| Rota | Método | Função |
| :--- | :---: | :--- |
| `/clientes` | GET | Listagem paginada (25 por página), filtros por texto/status e busca por ID (`?id=`) na Árvore B |
| `/clientes/cadastrar` | POST | Cadastro de cliente (ID único; ID e eSIM automáticos quando omitidos) |
| `/clientes/<id>/editar` | POST | Alteração de nome, e-mail e status |
| `/clientes/<id>/associar` | POST | Associação de eSIM (único por cliente) e pacote |
| `/consulta` | GET | Consulta integrada cliente × destino: Árvore B + Tabela Hash + compatibilidade do pacote |
| `/arvore-b` | GET | Instrumentação: árvore por níveis, caminho de busca, divisões e verificação de propriedades |

As rotas que alteram dados usam POST com Post/Redirect/Get.

### Integração Árvore B × Tabela Hash
Na consulta de **cliente 58372 → destino IT**, o sistema executa `arvore.buscar(58372)` (Maria Silva, `ESIM-83921`, pacote 102) e `tabela.buscar("IT")` (Itália, cobertura disponível, 5G). Em seguida, confere se a região do pacote (Europa) cobre a região do destino. Se o cliente não existe, não está ativo, não tem eSIM/pacote, se o país não é atendido ou o pacote não cobre a região, a tela lista cada pendência.

### Dados de clientes
O arquivo foi gerado por `gerar_clientes.py` (semente fixa, 1.000 clientes, IDs e eSIMs únicos, ordem embaralhada para provocar divisões em vários pontos da árvore). Para gerar de novo: `python gerar_clientes.py [quantidade] [semente]`. Uma pequena parcela dos clientes (82 no arquivo fornecido) nasce *pendente*, sem eSIM e sem pacote, para demonstrar a associação.

### Testes
```bash
python -m unittest discover -s tests -v
```
Os testes cobrem inserção aleatória/crescente/decrescente em vários graus, IDs duplicados, alteração, altura máxima teórica, instrumentação, detecção de corrupção e reconstrução idêntica a partir da ordem de inserção.

---

## 3.2 Etapa 3: Grafos e Integração Final

### Grafo (`estruturas/grafo.py`)
- **Modelo:** grafo ponderado e não-direcionado. **Vértice** = país da Tabela Hash (código de 2 letras); **aresta** = conexão com latência simulada em ms. A rede inicial (`arquivos/rede.json`) reproduz a figura do enunciado: BR–US 80, BR–PT 120, PT–ES 30, PT–FR 40, FR–IT 25, US–CA 20 e CA–JP 110.
- **Representação:** lista de adjacência (dicionário vértice → {vizinho: latência}), com cada aresta gravada nas duas pontas.
- **Coerência com as outras etapas:** os vértices são sempre os países da Tabela Hash. Cadastrar um país cria um vértice isolado; remover um país apaga o vértice, suas arestas e as rotas em cache que o usavam.
- **BFS:** fila FIFO; devolve ordem, camadas (saltos), pai de cada vértice e vértices não alcançados. O(V + E).
- **DFS:** pilha explícita (iterativa, mesma ordem da versão recursiva); devolve ordem, profundidade, pai e tempos de descoberta/finalização. O(V + E).
- **Dijkstra:** menor soma de latências, com **min-heap binário próprio** (`FilaPrioridade`) e remoção preguiçosa de entradas obsoletas; para ao finalizar o destino. Devolve caminho, latência, ordem de expansão, nós expandidos, relaxamentos e arestas examinadas. O((V + E) log V). Pesos devem ser positivos (validado ao criar a aresta).
- Os vizinhos são sempre visitados em ordem alfabética, tornando as execuções determinísticas.
- **Visualização:** a página `/rede` desenha o grafo em SVG (posições do enunciado), destacando a rota de menor latência ou a árvore de BFS/DFS e numerando os vértices pela ordem de visita/expansão. Também exibe métricas (vértices, arestas, densidade, componentes conexos, graus), a lista de adjacência e a comparação entre o caminho com menos saltos (BFS) e o de menor latência (Dijkstra).

### Consulta final integrada (`/consulta`)
1. **Árvore B:** busca o cliente pelo ID. 2. **Tabela Hash:** verifica se o destino (e a origem) é atendido. 3. **Pacotes:** o pacote do cliente cobre a região do destino? 4. **Grafo:** localiza origem e destino e calcula a rota de menor latência com Dijkstra **via Cache LRU**. 5. **Resultado** no formato do enunciado. O país de origem é um campo da consulta (padrão: Brasil).

Exemplo: cliente `58372`, origem `BR`, destino `IT` → Maria Silva, `ESIM-83921`, Europa Plus (10 GB, 30 dias), Itália com cobertura 5G, melhor rota **Brasil → Portugal → França → Itália, 185 ms**. A primeira consulta é um *cache miss* (executa o Dijkstra); as seguintes são *hits*.

### Rotas da Etapa 3
| Rota | Método | Função |
| :--- | :---: | :--- |
| `/rede` | GET | Visualização do grafo; `?bfs=BR`, `?dfs=BR`, `?de=BR&para=IT[&cache=0]` |
| `/rede/arestas/salvar` | POST | Cria uma conexão ou altera a latência (invalida todo o cache) |
| `/rede/arestas/remover` | POST | Remove uma conexão (invalida todo o cache) |
| `/cache` | GET | Painel do Cache LRU: lista MRU → LRU, métricas, eventos e benchmark |
| `/cache/configurar` | POST | Altera capacidade (1 a 1000) e TTL |
| `/cache/limpar` | POST | Esvazia o cache |
| `/cache/benchmark` | POST | Executa o benchmark (não altera o cache real) |
| `/consulta` | GET | Agora inclui origem e a rota de menor latência |

As rotas que alteram dados usam POST com Post/Redirect/Get. O cache é **volátil** (só existe em memória), enquanto as arestas são persistidas em `rede.json`.

### Testes
```bash
python -m unittest discover -s tests -v
```
Além dos testes da Árvore B, cobrem o Grafo (incluindo o Dijkstra conferido por força bruta e o DFS iterativo conferido contra a versão recursiva), o Cache LRU (inclusive contra um modelo de referência com 5.000 operações aleatórias), a invalidação, o benchmark e as rotas Flask.

---

## 4. Instruções de Execução

### Pré-requisitos
- Python 3.10 ou superior
- Gerenciador de pacotes `pip`

### 1. Clonar o repositório
```bash
git clone https://github.com/take071/TrabalhoED2.git
cd TrabalhoED2
```

### 2. Criar e ativar o ambiente virtual (venv)

**No Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**No Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*(No Prompt de Comando / CMD tradicional: `venv\Scripts\activate.bat`)*

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 4. Executar a aplicação
```bash
python3 app.py   # ou python app.py no Windows
```

A aplicação ficará disponível em: **`http://localhost:5000`**

> 💡 **Nota (Nix / NixOS):** Para desenvolvedores que utilizam NixOS, o repositório também inclui suporte opcional via `nix-shell`. Basta rodar `nix-shell` e em seguida `python3 app.py`.
