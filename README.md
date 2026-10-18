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

## 3. Estrutura de Diretórios (Etapa 1)

O projeto é construído de forma incremental. Nesta primeira etapa, a estrutura foca na **Tabela Hash** e nos arquivos de países, mantendo os diretórios preparados para os próximos módulos:

```text
Trabalho-ED2/
├── app.py                     # Aplicação Flask e rotas da Etapa 1
├── shell.nix                  # Configuração de ambiente para Nix/NixOS
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
- Pip ou ambiente Nix

### Executando com ambiente virtual Python (padrão)
```bash
# Criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar as dependências
pip install -r requirements.txt

# Executar a aplicação
python3 app.py
```

### Executando via Nix / NixOS
```bash
nix-shell
python3 app.py
```

Após iniciar o servidor, a aplicação estará acessível em: `http://localhost:5000`
