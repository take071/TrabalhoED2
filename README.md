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

> 📋 **Acompanhamento da Etapa 1:** Consulte o [Roadmap & Checklist da Etapa 1](ETAPA_1_TODOS.md) para acompanhar o progresso detalhado, arquitetura e critérios de aceite das entregas.

---

## 2. Diferencial da Equipe

**Tema:** Sistema de Cache LRU (Least Recently Used) Customizado para Consultas de Rotas.

### Problema abordado
Em redes de telecomunicações, o cálculo de rotas de menor latência exige alto processamento computacional, especialmente ao realizar travessias complexas. Quando múltiplos clientes acessam destinos populares repetidas vezes (ex: do Brasil para a Itália), o sistema aciona recálculos redundantes do menor caminho. A ausência de um mecanismo de memória temporária aumenta o tempo de resposta da aplicação Web e desperdiça recursos de processamento ao resolver o mesmo problema diversas vezes.

### Como o diferencial se integra às estruturas do projeto
O sistema interceptará as consultas de conectividade solicitadas pelos clientes e atuará como uma camada de otimização em memória, integrando-se diretamente às três estruturas principais do projeto:

1. **Tabela Hash:** Além de a Tabela Hash gerenciar os dados dos países atendidos, sua mecânica de chave-valor inspira a estrutura interna do próprio Cache LRU (aliada a uma Fila Duplamente Encadeada para garantir buscas em tempo $O(1)$). Ademais, as funções de alteração e remoção de países na Tabela Hash principal do sistema atuarão como gatilhos: se a infraestrutura for alterada, o cache é invalidado para garantir que os clientes não recebam rotas desatualizadas.

2. **Grafo da Rede:** Atua como a fonte da verdade (*fallback*). O algoritmo de Dijkstra, projetado para calcular a soma mínima das latências nas arestas, só será executado em caso de *Cache Miss* (quando a rota solicitada ainda não foi pesquisada ou expirou). Após o Grafo calcular a rota de menor latência, o resultado é imediatamente gravado no Cache LRU para que as próximas consultas idênticas sejam respondidas sem necessidade de nova travessia nos vértices.

3. **Árvore B e Consulta Integrada:** Durante a Consulta Final Integrada exigida no projeto, o sistema busca o registro e o ID do cliente na Árvore B e verifica seu pacote. Na etapa de montar a resposta, em vez de onerar o servidor, o sistema devolve o caminho salvo instantaneamente a partir do cache, acelerando o retorno do painel para o cliente e demonstrando como uma quarta estrutura (Cache) suporta e agiliza a comunicação entre as Árvores e os Grafos.

---

## 3. Estrutura de Diretórios (Etapa 1)

O projeto é construído de forma incremental. Nesta primeira etapa, a estrutura foca na **Tabela Hash** e nos arquivos de países, mantendo os diretórios preparados para os próximos módulos:

```text
Trabalho-ED2/
├── app.py                     # Aplicação Flask e rotas da Etapa 1
├── shell.nix                  # (Opcional) Configuração de ambiente para Nix/NixOS
├── requirements.txt           # Dependências do projeto (Flask)
├── README.md                  # Documentação e relatório do projeto
│
├── estruturas/                # Implementação das estruturas de dados
│   ├── __init__.py
│   └── tabela_hash.py         # [Etapa 1] Tabela Hash própria com instrumentação
│
├── arquivos/                  # Persistência em disco (JSON)
│   └── paises.json            # [Etapa 1] Base de dados dos países atendidos
│
├── templates/                 # Templates Jinja2 (a serem desenvolvidos na Etapa 1)
│   └── .gitkeep
│
└── static/                    # Arquivos estáticos (CSS, JS, Imagens)
    ├── css/
    │   └── .gitkeep
    ├── img/
    │   └── logo.png           # Logotipo da GlobalSIM
    └── js/
        └── .gitkeep
```

*Nota: Os módulos das etapas seguintes (`arvore_b.py`, `clientes.json`, `pacotes.json`, `grafo.py`, `rede.json` e o `recomendador.py`) serão adicionados e integrados incrementalmente nas Etapas 2 e 3.*

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
