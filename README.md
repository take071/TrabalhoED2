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
- **Etapa 3 (Grafos):** Modelagem da rede internacional com cálculo de rotas de menor latência (BFS, DFS e Dijkstra).

A persistência dos dados é realizada em arquivos JSON, carregados nas estruturas em memória durante a inicialização da aplicação, mantendo a lógica das estruturas de dados estritamente separada das rotas e controladores do Flask.

> 📋 **Acompanhamento das Etapas:** Consulte os roadmaps detalhados na pasta [`etapas/`](etapas/):
> - [Roadmap & Checklist da Etapa 1 (Tabela Hash)](etapas/ETAPA_1_TODOS.md)
> - [Roadmap & Checklist da Etapa 2 (Árvore B)](etapas/ETAPA_2_TODOS.md)
> - [Roadmap & Checklist da Etapa 3 (Grafos & Recomendador)](etapas/ETAPA_3_TODOS.md)

---

## 2. Diferencial da Equipe

**Tema:** Recomendação de pacote de dados a partir do roteiro de viagem.

### Problema abordado
Viajantes que realizam viagens com múltiplos destinos frequentemente têm dificuldade para escolher o plano de dados mais econômico e adequado. Contratar pacotes individuais para cada país encarece a viagem, enquanto pacotes globais podem ser desnecessários quando o itinerário abrange apenas uma região específica.

### Como o diferencial se integra às estruturas do projeto
O sistema receberá o roteiro do usuário (países de destino, quantidade de dias e perfil de consumo) e utilizará as três estruturas implementadas:

1. **Tabela Hash:** Faz a verificação direta em tempo O(1) de cada país informado, checando se a GlobalSIM possui cobertura no destino, qual operadora e tecnologia estão disponíveis (4G/5G) e a qual região geográfica o país pertence.
2. **Grafo da Rede:** Analisa a rota da viagem, calculando a sequência de conexões e a latência estimada entre os pontos do itinerário.
3. **Árvore B e Catálogo de Pacotes:** Cruza as regiões dos países do roteiro, a duração total da viagem e o consumo previsto com os pacotes cadastrados. O algoritmo determina se pacotes regionais atendem à viagem ou se um pacote Global é a opção mais vantajosa, apresentando a melhor relação custo-benefício para o cliente.

---

## 3. Estrutura de Diretórios do Projeto

O projeto é construído de forma modular e incremental, organizando código-fonte, dados, testes, documentação e materiais acadêmicos:

```text
Trabalho-ED2/
├── app.py                     # Aplicação Web Flask principal e rotas
├── requirements.txt           # Dependências Python (Flask, Folium, Geopy)
├── shell.nix                  # Configuração de ambiente reprodutível (Nix/NixOS)
├── README.md                  # Documentação e relatório principal do projeto
├── .gitignore                 # Arquivos ignorados pelo controle de versão
│
├── estruturas/                # Núcleo das Estruturas de Dados (ED2)
│   ├── __init__.py
│   ├── tabela_hash.py         # [Etapa 1] Tabela Hash própria com encadeamento separado
│   └── arvore_b.py            # [Etapa 2] Esqueleto da Árvore B para clientes e eSIMs
│
├── arquivos/                  # Persistência em disco (JSON)
│   └── paises.json            # [Etapa 1] Base de dados dos países atendidos e coordenadas
│
├── templates/                 # Camada de apresentação (Jinja2 + Bootstrap 5)
│   ├── base.html              # Layout base com navegação e rodapé acadêmico
│   ├── index.html             # Dashboard principal com mapa dinâmico Folium
│   ├── cobertura.html         # Consulta em tempo O(1) com mapa do destino
│   ├── paises.html            # Gestão gerencial (CRUD) de destinos
│   └── instrumentacao.html    # Inspeção visual dos 17 buckets e simulação didática
│
├── static/                    # Arquivos estáticos servidos pelo Flask
│   ├── css/
│   │   └── style.css          # Design system e folhas de estilo customizadas
│   ├── js/                    # Scripts adicionais do frontend
│   └── img/
│       ├── logo.png           # Logotipo institucional da GlobalSIM
│       └── globe-routes.png   # Elementos gráficos da aplicação
│
├── etapas/                    # Roadmaps e backlogs de acompanhamento de cada etapa
│   ├── ETAPA_1_TODOS.md       # Checklist e documentação completa da Etapa 1
│   ├── ETAPA_2_TODOS.md       # Especificação e backlog da Etapa 2 (Árvore B)
│   └── ETAPA_3_TODOS.md       # Especificação e backlog da Etapa 3 (Grafos)
│
├── tests/                     # Testes unitários automatizados (unittest)
│   ├── __init__.py
│   └── test_tabela_hash.py    # Testes de inserção, busca, colisão, remoção e métricas
│
├── docs/                      # Materiais acadêmicos e referências da disciplina
│   ├── AULAS-ED-2.pdf         # Slides e notas de aula de Estruturas de Dados II
│   └── TrabalhoPratico-2026.2.pdf # Especificação formal do trabalho prático
│
└── scripts/                   # Scripts utilitários e testes manuais
    └── gerar_mapa_demo.py     # Script auxiliar de geração e teste do mapa Folium
```

---

## 4. Instruções de Execução

### Pré-requisitos
- Python 3.10 ou superior
- Gerenciador de pacotes `pip` (ou Nix/NixOS)

---

### Opção A: Execução no Nix / NixOS (Recomendado)

O repositório já inclui o arquivo `shell.nix` configurado com Python 3 e todas as dependências (`flask`, `folium`, `geopy`):

```bash
# Entrar no ambiente com as dependências carregadas:
nix-shell

# Executar a aplicação:
python3 app.py
```

Ou diretamente em um único comando:
```bash
nix-shell --run "python3 app.py"
```

---

### Opção B: Execução com Ambiente Virtual Padrão (`venv`)

#### 1. Criar e ativar o ambiente virtual

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

*(No Prompt de Comando tradicional: `venv\Scripts\activate.bat`)*

#### 2. Instalar as dependências
```bash
pip install -r requirements.txt
```

#### 3. Executar a aplicação
```bash
python3 app.py   # ou python app.py no Windows
```

A aplicação ficará disponível em: **`http://localhost:5000`**

---

## 5. Testes Unitários Automatizados

Para executar a suíte de testes unitários da Tabela Hash (verificação de colisões, inserção, remoção e religamento de ponteiros):

```bash
# Via Python padrão / venv:
python3 -m unittest discover tests

# Ou via NixOS:
nix-shell --run "python3 -m unittest discover tests"
```

## 5. Testes Unitários Automatizados

Para executar a suíte de testes unitários da Tabela Hash (verificação de colisões, inserção, remoção e religamento de ponteiros):

```bash
# Via Python padrão / venv:
python3 -m unittest discover tests

# Ou via NixOS:
nix-shell --run "python3 -m unittest discover tests"
```

