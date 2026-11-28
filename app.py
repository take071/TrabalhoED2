"""
Aplicação Principal - GlobalSIM (Etapas 1 e 2)
Disciplina: Estruturas de Dados II - UNEB
Docente: Profa. Maria Inés Restovic
Equipe: Arthur Felipe, Lucas Vinicius, Raphael Lopes

Escopo da Etapa 1:
- Tabela Hash própria para gerenciamento dos países atendidos.
- Consulta rápida de cobertura por código do país (ex: "BR", "IT").
- CRUD completo de países atendidos com persistência em arquivos/paises.json.
- Painel de instrumentação básica da estrutura (capacidade, colisões, fator de carga).
- Rotas de alteração de dados utilizando método POST (padrão Post/Redirect/Get).

Escopo da Etapa 2 (preservando integralmente a Etapa 1):
- Árvore B própria (estruturas/arvore_b.py) indexando ~1.000 clientes pelo ID.
- Cadastro, consulta por ID, listagem e alteração de clientes.
- Associação de eSIM e pacote de serviço ao cliente.
- Persistência dos clientes em arquivos/clientes.json (pacotes em arquivos/pacotes.json).
- Consulta integrada: Árvore B (cliente) x Tabela Hash (cobertura do país de destino).
- Painel de instrumentação da Árvore B (altura, nós, divisões, caminho de busca).

Escopo da Etapa 3 (preservando integralmente as Etapas 1 e 2):
- Grafo ponderado (estruturas/grafo.py) com a rede internacional; vértices = países da
  Tabela Hash e arestas = latências simuladas em ms (arquivos/rede.json).
- BFS, DFS e Dijkstra, com visualização do grafo (SVG) e instrumentação.
- Consulta final integrada: Árvore B (cliente) + Tabela Hash (destino) + pacote + Grafo (rota).
- DIFERENCIAL: Cache LRU customizado em O(1) (estruturas/cache_lru.py) que guarda as rotas
  calculadas pelo Dijkstra e é invalidado quando a rede ou os países mudam.
"""

import os
import re
import json
import math
import random
from flask import Flask, render_template, request, redirect, url_for, flash

from estruturas.tabela_hash import TabelaHash
from estruturas.arvore_b import ArvoreB
from estruturas.grafo import Grafo
from estruturas.cache_lru import CacheLRU
from estruturas.servico_rotas import ServicoRotas, executar_benchmark

app = Flask(__name__)
app.secret_key = "globalsim-ed2-secret-key"

# Caminho para o arquivo de persistência dos países (Etapa 1)
PAISES_JSON_PATH = os.path.join(os.path.dirname(__file__), "arquivos", "paises.json")

# Caminhos de persistência da Etapa 2
CLIENTES_JSON_PATH = os.path.join(os.path.dirname(__file__), "arquivos", "clientes.json")
PACOTES_JSON_PATH = os.path.join(os.path.dirname(__file__), "arquivos", "pacotes.json")

# Caminho de persistência da Etapa 3 (arestas da rede)
REDE_JSON_PATH = os.path.join(os.path.dirname(__file__), "arquivos", "rede.json")

# Instância da Tabela Hash em memória (Etapa 1)
tabela_paises = TabelaHash(capacidade_inicial=17)

# Árvore B em memória (Etapa 2): chave = ID do cliente; grau mínimo t = 3
# (cada nó guarda de 2 a 5 chaves, exceto a raiz, e tem até 6 filhos)
GRAU_MINIMO_ARVORE_B = 3
arvore_clientes = ArvoreB(grau_minimo=GRAU_MINIMO_ARVORE_B)

# Pacotes de serviço: não são uma estrutura principal, então uma lista simples basta
pacotes = []

# Grafo da rede internacional (Etapa 3): os vértices são os países da Tabela Hash
grafo_rede = Grafo()

# Diferencial: Cache LRU de rotas (volátil, só existe em memória) + serviço que o integra ao Grafo
CAPACIDADE_CACHE_PADRAO = 8
cache_rotas = CacheLRU(capacidade=CAPACIDADE_CACHE_PADRAO)
servico_rotas = ServicoRotas(grafo_rede, cache_rotas)
ultimo_benchmark = None
ORIGEM_PADRAO = "BR"

STATUS_VALIDOS = ("ativo", "inativo", "suspenso", "pendente")
CLIENTES_POR_PAGINA = 25
REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
REGEX_ESIM = re.compile(r"^ESIM-\d{4,10}$")


def carregar_dados():
    """
    Carrega os dados de arquivos/paises.json para a Tabela Hash em memória.
    Executado na inicialização da aplicação.
    """
    if os.path.exists(PAISES_JSON_PATH):
        try:
            with open(PAISES_JSON_PATH, "r", encoding="utf-8") as f:
                dados = json.load(f)
                for item in dados:
                    if "codigo" in item:
                        tabela_paises.inserir(item["codigo"], item)
        except Exception as e:
            print(f"Erro ao carregar dados de {PAISES_JSON_PATH}: {e}")


def persistir_dados():
    """
    Persiste o estado atual da Tabela Hash de volta no arquivo arquivos/paises.json.
    Executado após operações de cadastro, alteração ou remoção.
    """
    try:
        lista_paises = tabela_paises.listar_todos()
        with open(PAISES_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(lista_paises, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao persistir dados em {PAISES_JSON_PATH}: {e}")


def carregar_pacotes():
    """Carrega os pacotes de serviço de arquivos/pacotes.json."""
    pacotes.clear()
    if os.path.exists(PACOTES_JSON_PATH):
        try:
            with open(PACOTES_JSON_PATH, "r", encoding="utf-8") as f:
                pacotes.extend(json.load(f))
        except Exception as e:
            print(f"Erro ao carregar dados de {PACOTES_JSON_PATH}: {e}")


def carregar_clientes():
    """
    Carrega arquivos/clientes.json para a Árvore B em memória (inserção um a um,
    na ordem do arquivo). IDs duplicados ou inválidos são ignorados.
    """
    if not os.path.exists(CLIENTES_JSON_PATH):
        return
    try:
        with open(CLIENTES_JSON_PATH, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar dados de {CLIENTES_JSON_PATH}: {e}")
        return

    ignorados = 0
    for item in dados:
        try:
            if not arvore_clientes.inserir(item["id"], item):
                ignorados += 1
        except (KeyError, TypeError, ValueError):
            ignorados += 1
    if ignorados:
        print(f"Aviso: {ignorados} registro(s) de cliente ignorado(s) na carga (duplicados/inválidos).")


def persistir_clientes():
    """
    Persiste a Árvore B em arquivos/clientes.json, na ORDEM DE INSERÇÃO. Assim, ao
    reiniciar, a carga reconstrói exatamente a mesma árvore (mesma altura, mesmos nós
    e mesmas divisões), o que mantém a instrumentação estável entre execuções.
    A gravação é atômica: escreve em arquivo temporário e substitui o original,
    evitando corromper o JSON caso o processo seja interrompido no meio da escrita.
    """
    temporario = CLIENTES_JSON_PATH + ".tmp"
    try:
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(arvore_clientes.listar_em_ordem_de_insercao(), f, indent=2, ensure_ascii=False)
        os.replace(temporario, CLIENTES_JSON_PATH)
    except Exception as e:
        print(f"Erro ao persistir dados em {CLIENTES_JSON_PATH}: {e}")


def carregar_rede():
    """
    Monta o Grafo: um vértice para cada país da Tabela Hash e as arestas de
    arquivos/rede.json. Arestas que citam países inexistentes são ignoradas.
    """
    for pais in tabela_paises.listar_todos():
        grafo_rede.adicionar_vertice(pais["codigo"])
    if not os.path.exists(REDE_JSON_PATH):
        return
    try:
        with open(REDE_JSON_PATH, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar dados de {REDE_JSON_PATH}: {e}")
        return
    ignoradas = 0
    for item in dados.get("arestas", []):
        try:
            grafo_rede.adicionar_aresta(item["origem"], item["destino"], item["latencia"])
        except (KeyError, TypeError, ValueError):
            ignoradas += 1
    if ignoradas:
        print(f"Aviso: {ignoradas} aresta(s) ignorada(s) na carga da rede (países inexistentes/inválidos).")


def persistir_rede():
    """Grava as arestas do Grafo em arquivos/rede.json (escrita atômica)."""
    temporario = REDE_JSON_PATH + ".tmp"
    try:
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(grafo_rede.para_dict(), f, indent=2, ensure_ascii=False)
        os.replace(temporario, REDE_JSON_PATH)
    except Exception as e:
        print(f"Erro ao persistir dados em {REDE_JSON_PATH}: {e}")


# Carga inicial dos dados
carregar_dados()
carregar_pacotes()
carregar_clientes()
carregar_rede()


# ==============================================================================
# FUNÇÕES AUXILIARES DA ETAPA 2
# ==============================================================================

def obter_pacote(codigo):
    """Retorna o pacote de serviço pelo código (ou None)."""
    for pacote in pacotes:
        if pacote["codigo"] == codigo:
            return pacote
    return None


def interpretar_id(texto):
    """Converte o texto de um ID de cliente em inteiro positivo; None se inválido."""
    texto = (texto or "").strip()
    if texto.isdigit() and 0 < int(texto) < 10**9:
        return int(texto)
    return None


def esims_em_uso(ignorar_id=None):
    """Conjunto de eSIMs já associados a clientes (garante unicidade do eSIM)."""
    return {
        c["esim"] for c in arvore_clientes.listar_todos()
        if c.get("esim") and c["id"] != ignorar_id
    }


def gerar_esim(em_uso):
    """Gera um código de eSIM no formato ESIM-##### que ainda não esteja em uso."""
    while True:
        candidato = f"ESIM-{random.randint(10000, 99999)}"
        if candidato not in em_uso:
            return candidato


def gerar_id_cliente():
    """Gera um ID de 5 dígitos livre, verificando a existência na Árvore B."""
    while True:
        candidato = random.randint(10000, 99999)
        if not arvore_clientes.contem(candidato):
            return candidato


def pacote_cobre_regiao(pacote, regiao):
    """Um pacote cobre o destino se for Global ou da mesma região do país."""
    return pacote["regiao"] == "Global" or pacote["regiao"] == regiao


# ==============================================================================
# ROTAS DA ETAPA 1
# ==============================================================================

@app.route("/")
def index():
    """Página inicial do GlobalSIM com visão geral e atalhos rápidos."""
    metricas = tabela_paises.obter_metricas()
    metricas_arvore = arvore_clientes.obter_metricas()
    return render_template(
        "index.html",
        metricas=metricas,
        metricas_arvore=metricas_arvore,
        metricas_grafo=grafo_rede.obter_metricas(),
        metricas_cache=cache_rotas.obter_metricas(),
    )


@app.route("/cobertura", methods=["GET", "POST"])
def cobertura():
    """
    Consulta de cobertura por código de país (ex: "BR", "IT").
    A verificação deve ser feita diretamente na Tabela Hash em tempo O(1).
    """
    resultado = None
    codigo_buscado = ""
    consultado = False

    if request.method == "POST":
        consultado = True
        codigo_buscado = request.form.get("codigo", "").strip().upper()
        if codigo_buscado:
            resultado = tabela_paises.buscar(codigo_buscado)

    return render_template(
        "cobertura.html",
        resultado=resultado,
        codigo=codigo_buscado,
        consultado=consultado
    )


@app.route("/paises")
def paises():
    """Listagem de todos os países atendidos cadastrados na Tabela Hash."""
    lista_paises = tabela_paises.listar_todos()
    return render_template("paises.html", paises=lista_paises)


@app.route("/paises/cadastrar", methods=["POST"])
def cadastrar_pais():
    """
    Cadastra um novo país na Tabela Hash e persiste no JSON.
    Padrão Post/Redirect/Get.
    """
    codigo = request.form.get("codigo", "").strip().upper()
    pais = request.form.get("pais", "").strip()
    regiao = request.form.get("regiao", "").strip()
    operadora = request.form.get("operadora", "").strip()
    tecnologia = request.form.get("tecnologia", "5G").strip().upper()

    if not codigo or not pais or not regiao or not operadora or not tecnologia:
        flash("Todos os campos são obrigatórios para o cadastro!", "danger")
        return redirect(url_for("paises"))

    existente = tabela_paises.buscar(codigo)
    novo_pais = {
        "codigo": codigo,
        "pais": pais,
        "regiao": regiao,
        "operadora": operadora,
        "tecnologia": tecnologia
    }

    tabela_paises.inserir(codigo, novo_pais)
    persistir_dados()
    grafo_rede.adicionar_vertice(codigo)   # novo país entra na rede (isolado, sem arestas)

    if existente:
        flash(f"O país com código '{codigo}' já existia e foi atualizado com sucesso!", "info")
    else:
        flash(f"País '{pais}' ({codigo}) cadastrado com sucesso!", "success")

    return redirect(url_for("paises"))


@app.route("/paises/<codigo>/editar", methods=["POST"])
def editar_pais(codigo):
    """
    Atualiza os dados de um país existente na Tabela Hash e persiste no JSON.
    """
    codigo = codigo.strip().upper()
    pais = request.form.get("pais", "").strip()
    regiao = request.form.get("regiao", "").strip()
    operadora = request.form.get("operadora", "").strip()
    tecnologia = request.form.get("tecnologia", "5G").strip().upper()

    if not pais or not regiao or not operadora or not tecnologia:
        flash("Todos os campos são obrigatórios para a edição!", "danger")
        return redirect(url_for("paises"))

    dados_atualizados = {
        "codigo": codigo,
        "pais": pais,
        "regiao": regiao,
        "operadora": operadora,
        "tecnologia": tecnologia
    }

    tabela_paises.inserir(codigo, dados_atualizados)
    persistir_dados()
    grafo_rede.adicionar_vertice(codigo)   # no-op se já existe; garante vértice para todo país
    flash(f"Dados do país {codigo} ({pais}) atualizados com sucesso!", "success")
    return redirect(url_for("paises"))


@app.route("/paises/<codigo>/excluir", methods=["POST"])
def excluir_pais(codigo):
    """
    Remove um país da Tabela Hash e atualiza o arquivo JSON.
    """
    codigo = codigo.strip().upper()
    removido = tabela_paises.remover(codigo)

    if removido:
        persistir_dados()
        # Gatilho do diferencial: o país sai da rede e as rotas em cache que o usam são invalidadas
        grafo_rede.remover_vertice(codigo)
        persistir_rede()
        invalidadas = servico_rotas.invalidar_pais(codigo)
        complemento = f" {invalidadas} rota(s) em cache foram invalidadas." if invalidadas else ""
        flash(f"País '{codigo}' removido com sucesso! Suas conexões na rede também foram removidas.{complemento}", "warning")
    else:
        flash(f"País com código '{codigo}' não encontrado para remoção.", "danger")

    return redirect(url_for("paises"))


@app.route("/instrumentacao")
def instrumentacao():
    """
    Exibe as métricas de instrumentação interna da Tabela Hash
    (fator de carga, colisões, capacidade e distribuição dos buckets).
    """
    metricas = tabela_paises.obter_metricas()
    return render_template("instrumentacao.html", metricas=metricas)


# ==============================================================================
# ROTAS DA ETAPA 2 - CLIENTES (ÁRVORE B)
# ==============================================================================

@app.route("/clientes")
def clientes():
    """
    Gerenciamento de clientes.
    - ?id=...: consulta por ID diretamente na Árvore B (com caminho percorrido).
    - ?q=...&status=...: filtros da listagem (percurso em ordem da Árvore B).
    - ?pagina=...: paginação da listagem.
    """
    id_buscado = request.args.get("id", "").strip()
    busca = None
    if id_buscado:
        id_numerico = interpretar_id(id_buscado)
        if id_numerico is None:
            busca = {"id": id_buscado, "invalido": True, "cliente": None, "instrumentacao": None}
        else:
            cliente = arvore_clientes.buscar(id_numerico)
            busca = {
                "id": id_numerico,
                "invalido": False,
                "cliente": cliente,
                "instrumentacao": arvore_clientes.ultima_busca,
            }

    termo = request.args.get("q", "").strip().lower()
    status = request.args.get("status", "").strip().lower()

    lista = arvore_clientes.listar_todos()
    if termo:
        lista = [
            c for c in lista
            if termo in c["nome"].lower() or termo in c["email"].lower()
            or termo in (c.get("esim") or "").lower() or termo in str(c["id"])
        ]
    if status in STATUS_VALIDOS:
        lista = [c for c in lista if c["status"] == status]

    total_filtrado = len(lista)
    total_paginas = max(1, math.ceil(total_filtrado / CLIENTES_POR_PAGINA))
    try:
        pagina = int(request.args.get("pagina", 1))
    except ValueError:
        pagina = 1
    pagina = min(max(pagina, 1), total_paginas)
    inicio = (pagina - 1) * CLIENTES_POR_PAGINA

    return render_template(
        "clientes.html",
        busca=busca,
        clientes=lista[inicio:inicio + CLIENTES_POR_PAGINA],
        total_filtrado=total_filtrado,
        total_geral=len(arvore_clientes),
        pagina=pagina,
        total_paginas=total_paginas,
        q=request.args.get("q", "").strip(),
        status_filtro=status,
        status_validos=STATUS_VALIDOS,
        pacotes=pacotes,
        nomes_pacotes={p["codigo"]: p["nome"] for p in pacotes},
        metricas_arvore=arvore_clientes.obter_metricas(),
    )


@app.route("/clientes/cadastrar", methods=["POST"])
def cadastrar_cliente():
    """
    Cadastra um novo cliente na Árvore B e persiste no JSON.
    - ID opcional (gerado automaticamente se vazio); deve ser único.
    - Se um pacote for informado, um eSIM é gerado e o cliente fica 'ativo';
      caso contrário, fica 'pendente' até a associação de eSIM e pacote.
    """
    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip()
    id_texto = request.form.get("id", "").strip()
    pacote_texto = request.form.get("pacote", "").strip()

    if not nome or not email:
        flash("Nome e e-mail são obrigatórios para o cadastro de cliente.", "danger")
        return redirect(url_for("clientes"))
    if not REGEX_EMAIL.match(email):
        flash(f"O e-mail '{email}' não é válido.", "danger")
        return redirect(url_for("clientes"))

    if id_texto:
        cliente_id = interpretar_id(id_texto)
        if cliente_id is None:
            flash("O ID deve ser um número inteiro positivo (ex: 58372).", "danger")
            return redirect(url_for("clientes"))
        if arvore_clientes.contem(cliente_id):
            flash(f"Já existe um cliente com o ID {cliente_id}. O ID deve ser único.", "danger")
            return redirect(url_for("clientes", id=cliente_id))
    else:
        cliente_id = gerar_id_cliente()

    esim, pacote_codigo, status = None, None, "pendente"
    if pacote_texto:
        pacote = obter_pacote(int(pacote_texto)) if pacote_texto.isdigit() else None
        if pacote is None:
            flash(f"Pacote '{pacote_texto}' não encontrado.", "danger")
            return redirect(url_for("clientes"))
        pacote_codigo = pacote["codigo"]
        esim = gerar_esim(esims_em_uso())
        status = "ativo"

    arvore_clientes.inserir(cliente_id, {
        "id": cliente_id,
        "nome": nome,
        "email": email,
        "esim": esim,
        "pacote": pacote_codigo,
        "status": status,
    })
    persistir_clientes()

    divisoes = arvore_clientes.ultima_insercao["divisoes"]
    complemento = f" A inserção provocou {divisoes} divisão(ões) de nó." if divisoes else ""
    flash(f"Cliente '{nome}' cadastrado com o ID {cliente_id}.{complemento}", "success")
    return redirect(url_for("clientes", id=cliente_id))


@app.route("/clientes/<int:cliente_id>/editar", methods=["POST"])
def editar_cliente(cliente_id):
    """Altera nome, e-mail e status de um cliente existente (o ID não pode mudar)."""
    cliente = arvore_clientes.buscar(cliente_id)
    if cliente is None:
        flash(f"Cliente com ID {cliente_id} não encontrado.", "danger")
        return redirect(url_for("clientes"))

    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip()
    status = request.form.get("status", "").strip().lower()

    if not nome or not email or status not in STATUS_VALIDOS:
        flash("Nome, e-mail e um status válido são obrigatórios para a edição.", "danger")
        return redirect(url_for("clientes", id=cliente_id))
    if not REGEX_EMAIL.match(email):
        flash(f"O e-mail '{email}' não é válido.", "danger")
        return redirect(url_for("clientes", id=cliente_id))
    if status == "ativo" and not (cliente.get("esim") and cliente.get("pacote")):
        flash("Para ativar o cliente, associe antes um eSIM e um pacote.", "danger")
        return redirect(url_for("clientes", id=cliente_id))

    atualizado = dict(cliente, nome=nome, email=email, status=status)
    arvore_clientes.atualizar(cliente_id, atualizado)
    persistir_clientes()
    flash(f"Dados do cliente {cliente_id} ({nome}) atualizados com sucesso!", "success")
    return redirect(url_for("clientes", id=cliente_id))


@app.route("/clientes/<int:cliente_id>/associar", methods=["POST"])
def associar_cliente(cliente_id):
    """
    Associa um eSIM e um pacote de serviço ao cliente.
    - eSIM em branco: mantém o atual ou gera um novo, garantindo unicidade.
    - Cliente 'pendente' passa a 'ativo' após a associação.
    """
    cliente = arvore_clientes.buscar(cliente_id)
    if cliente is None:
        flash(f"Cliente com ID {cliente_id} não encontrado.", "danger")
        return redirect(url_for("clientes"))

    pacote_texto = request.form.get("pacote", "").strip()
    esim = request.form.get("esim", "").strip().upper()

    pacote = obter_pacote(int(pacote_texto)) if pacote_texto.isdigit() else None
    if pacote is None:
        flash("Selecione um pacote de serviço válido.", "danger")
        return redirect(url_for("clientes", id=cliente_id))

    if esim:
        if not REGEX_ESIM.match(esim):
            flash("O eSIM deve seguir o formato ESIM-12345.", "danger")
            return redirect(url_for("clientes", id=cliente_id))
        if esim in esims_em_uso(ignorar_id=cliente_id):
            flash(f"O eSIM {esim} já está associado a outro cliente.", "danger")
            return redirect(url_for("clientes", id=cliente_id))
    else:
        esim = cliente.get("esim") or gerar_esim(esims_em_uso())

    novo_status = "ativo" if cliente["status"] == "pendente" else cliente["status"]
    atualizado = dict(cliente, esim=esim, pacote=pacote["codigo"], status=novo_status)
    arvore_clientes.atualizar(cliente_id, atualizado)
    persistir_clientes()
    flash(f"{esim} e o pacote {pacote['nome']} foram associados ao cliente {cliente_id}.", "success")
    return redirect(url_for("clientes", id=cliente_id))


# ==============================================================================
# ROTA DA ETAPA 2 - INSTRUMENTAÇÃO DA ÁRVORE B
# ==============================================================================

@app.route("/arvore-b")
def arvore_b():
    """
    Exibe a instrumentação da Árvore B: grau, altura, nós por nível, ocupação,
    divisões e o caminho percorrido na busca por um ID (?id=...).
    """
    id_buscado = request.args.get("id", "").strip()
    busca = None
    if id_buscado:
        id_numerico = interpretar_id(id_buscado)
        if id_numerico is None:
            busca = {"id": id_buscado, "invalido": True}
        else:
            cliente = arvore_clientes.buscar(id_numerico)
            busca = {
                "id": id_numerico,
                "invalido": False,
                "cliente": cliente,
                "instrumentacao": arvore_clientes.ultima_busca,
            }

    metricas_arvore = arvore_clientes.obter_metricas()
    ok, mensagem_validacao = arvore_clientes.validar()

    caminho = set()
    if busca and not busca["invalido"]:
        caminho = set(busca["instrumentacao"]["caminho"])

    # Para manter a página leve, cada nível exibe no máximo 12 nós
    # (os nós do caminho da busca são sempre exibidos).
    limite_por_nivel = 12
    niveis_exibidos = []
    for indice, nos in enumerate(arvore_clientes.niveis()):
        exibidos = []
        for no in nos:
            if len(exibidos) < limite_por_nivel or no["id"] in caminho:
                exibidos.append(no)
        niveis_exibidos.append({
            "nivel": indice,
            "total_nos": len(nos),
            "total_chaves": sum(len(n["chaves"]) for n in nos),
            "nos": exibidos,
            "ocultos": len(nos) - len(exibidos),
        })

    n = metricas_arvore["tamanho"]
    t = metricas_arvore["grau_minimo"]
    altura_maxima = math.floor(math.log((n + 1) / 2, t)) + 1 if n > 0 else 0

    return render_template(
        "arvore_b.html",
        metricas=metricas_arvore,
        niveis=niveis_exibidos,
        busca=busca,
        caminho=caminho,
        valida=ok,
        mensagem_validacao=mensagem_validacao,
        altura_maxima=altura_maxima,
    )


# ==============================================================================
# ROTA DA ETAPA 2 - CONSULTA INTEGRADA (ÁRVORE B x TABELA HASH)
# ==============================================================================

@app.route("/consulta")
def consulta():
    """
    Consulta integrada cliente x destino x rede (somente leitura, por isso GET):
      1. Árvore B:      buscar(id_cliente)  -> cliente, eSIM, pacote e status
      2. Tabela Hash:   buscar(destino)     -> cobertura e tecnologia do país
      3. Pacotes:       o pacote do cliente cobre a região do destino?
      4. Grafo:         origem -> destino por Dijkstra, intermediado pelo Cache LRU (HIT/MISS)
    """
    cliente_raw = request.args.get("cliente", "").strip()
    destino_raw = request.args.get("destino", "").strip().upper()
    origem_raw = request.args.get("origem", "").strip().upper() or ORIGEM_PADRAO
    consultado = bool(cliente_raw or destino_raw)

    resultado = None
    if cliente_raw and destino_raw:
        cliente_id = interpretar_id(cliente_raw)
        cliente = arvore_clientes.buscar(cliente_id) if cliente_id else None
        instrumentacao_arvore = arvore_clientes.ultima_busca if cliente_id else None

        pais = tabela_paises.buscar(destino_raw)
        pacote = obter_pacote(cliente["pacote"]) if cliente and cliente.get("pacote") else None

        pendencias = []
        if cliente_id is None:
            pendencias.append("O ID informado não é um número válido.")
        elif cliente is None:
            pendencias.append(f"Cliente {cliente_id} não encontrado na Árvore B.")
        else:
            if cliente["status"] != "ativo":
                pendencias.append(f"O cliente está com status '{cliente['status']}'.")
            if not cliente.get("esim"):
                pendencias.append("O cliente ainda não possui eSIM associado.")
            if pacote is None:
                pendencias.append("O cliente não possui pacote de serviço associado.")
        if pais is None:
            pendencias.append(f"O destino '{destino_raw}' não é atendido (ausente na Tabela Hash).")
        compativel = None
        if pacote and pais:
            compativel = pacote_cobre_regiao(pacote, pais["regiao"])
            if not compativel:
                pendencias.append(
                    f"O pacote {pacote['nome']} ({pacote['regiao']}) não cobre {pais['pais']} ({pais['regiao']})."
                )

        # Etapa 3: origem e destino no Grafo + menor latência (Dijkstra via Cache LRU)
        origem_pais = tabela_paises.buscar(origem_raw)
        rota = None
        if origem_pais is None:
            pendencias.append(f"A origem '{origem_raw}' não é atendida (ausente na Tabela Hash).")
        elif pais is not None and grafo_rede.tem_vertice(origem_raw) and grafo_rede.tem_vertice(destino_raw):
            rota = servico_rotas.consultar(origem_raw, destino_raw)
            if not rota["encontrada"]:
                pendencias.append(f"Não há rota na rede entre {origem_pais['pais']} e {pais['pais']}.")

        resultado = {
            "cliente_id": cliente_id,
            "cliente": cliente,
            "arvore": instrumentacao_arvore,
            "origem": origem_raw,
            "origem_pais": origem_pais,
            "destino": destino_raw,
            "pais": pais,
            "pacote": pacote,
            "compativel": compativel,
            "rota": rota,
            "pendencias": pendencias,
            "apto": not pendencias,
        }

    return render_template(
        "consulta.html",
        resultado=resultado,
        consultado=consultado,
        cliente_valor=cliente_raw,
        destino_valor=destino_raw,
        origem_valor=origem_raw,
        nomes=nomes_paises(),
        paises=sorted(tabela_paises.listar_todos(), key=lambda p: p["pais"]),
    )



# ==============================================================================
# FUNÇÕES AUXILIARES DA ETAPA 3
# ==============================================================================

# Posições (x, y) dos vértices na visualização SVG, seguindo o desenho do enunciado.
# Países cadastrados depois que não estejam aqui são dispostos em uma fileira inferior.
POSICOES_REDE = {
    "BR": (170, 70), "US": (560, 70),
    "PT": (170, 220), "CA": (560, 220),
    "ES": (60, 360), "FR": (280, 360), "JP": (650, 360),
    "IT": (280, 480),
}


def nomes_paises():
    """Dicionário código -> nome do país, lido da Tabela Hash."""
    return {p["codigo"]: p["pais"] for p in tabela_paises.listar_todos()}


def montar_svg_rede(arestas_destacadas=None, ordem=None, origem=None, destino=None):
    """
    Calcula as coordenadas para desenhar o Grafo em SVG (renderizado pelo Jinja).
    - arestas_destacadas: conjunto de frozenset({u, v}) a realçar (rota ou árvore da busca).
    - ordem: dicionário vértice -> número de visita (BFS/DFS) ou de expansão (Dijkstra).
    """
    arestas_destacadas = arestas_destacadas or set()
    ordem = ordem or {}
    nomes = nomes_paises()

    posicoes, extras = {}, 0
    for v in grafo_rede.vertices():
        if v in POSICOES_REDE:
            posicoes[v] = POSICOES_REDE[v]
        else:
            posicoes[v] = (430 + 90 * (extras % 4), 430 + 60 * (extras // 4))
            extras += 1

    nos = [{
        "codigo": v, "nome": nomes.get(v, v), "x": x, "y": y,
        "ordem": ordem.get(v),
        "papel": "origem" if v == origem else ("destino" if v == destino else ""),
        "visitado": v in ordem,
    } for v, (x, y) in posicoes.items()]

    arestas = []
    for u, v, peso in grafo_rede.arestas():
        (x1, y1), (x2, y2) = posicoes[u], posicoes[v]
        arestas.append({
            "u": u, "v": v, "peso": peso,
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "mx": (x1 + x2) / 2, "my": (y1 + y2) / 2,
            "destaque": frozenset((u, v)) in arestas_destacadas,
        })

    altura = max([y for _, y in posicoes.values()] + [0]) + 70
    return {"nos": nos, "arestas": arestas, "altura": max(altura, 540)}


def arestas_da_arvore(pai):
    """Arestas (pai, filho) da árvore gerada por BFS/DFS."""
    return {frozenset((v, p)) for v, p in pai.items() if p is not None}


def arestas_do_caminho(caminho):
    return {frozenset(par) for par in zip(caminho, caminho[1:])}


# ==============================================================================
# ROTAS DA ETAPA 3 - REDE (GRAFO)
# ==============================================================================

@app.route("/rede")
def rede():
    """
    Visualização do Grafo e execução dos algoritmos (somente leitura, GET):
      ?bfs=BR         -> busca em largura a partir do país
      ?dfs=BR         -> busca em profundidade a partir do país
      ?de=BR&para=IT  -> Dijkstra (menor latência) via Cache LRU; &cache=0 ignora o cache
    """
    vertices = grafo_rede.vertices()
    nomes = nomes_paises()
    erros, res_bfs, res_dfs, res_rota, comparacao = {}, None, None, None, None
    destaque, ordem, origem_svg, destino_svg = set(), {}, None, None

    bfs_origem = request.args.get("bfs", "").strip().upper()
    dfs_origem = request.args.get("dfs", "").strip().upper()
    de = request.args.get("de", "").strip().upper()
    para = request.args.get("para", "").strip().upper()
    usar_cache = request.args.get("cache", "1") != "0"

    if bfs_origem:
        if grafo_rede.tem_vertice(bfs_origem):
            res_bfs = grafo_rede.bfs(bfs_origem)
            ordem = {v: i + 1 for i, v in enumerate(res_bfs["ordem"])}
            destaque, origem_svg = arestas_da_arvore(res_bfs["pai"]), bfs_origem
        else:
            erros["bfs"] = f"O país '{bfs_origem}' não existe na rede."
    elif dfs_origem:
        if grafo_rede.tem_vertice(dfs_origem):
            res_dfs = grafo_rede.dfs(dfs_origem)
            ordem = {v: i + 1 for i, v in enumerate(res_dfs["ordem"])}
            destaque, origem_svg = arestas_da_arvore(res_dfs["pai"]), dfs_origem
        else:
            erros["dfs"] = f"O país '{dfs_origem}' não existe na rede."
    elif de or para:
        if not grafo_rede.tem_vertice(de) or not grafo_rede.tem_vertice(para):
            erros["rota"] = "Informe dois países que existam na rede."
        else:
            res_rota = servico_rotas.consultar(de, para, usar_cache=usar_cache)
            origem_svg, destino_svg = de, para
            ordem = {e["vertice"]: i + 1 for i, e in enumerate(res_rota["ordem_expansao"])}
            if res_rota["encontrada"]:
                destaque = arestas_do_caminho(res_rota["caminho"])
                # Comparação didática: menor nº de saltos (BFS) x menor latência (Dijkstra)
                saltos = grafo_rede.caminho_menos_saltos(de, para)
                comparacao = {
                    "caminho_saltos": saltos,
                    "latencia_saltos": grafo_rede.latencia_do_caminho(saltos),
                    "igual": saltos == res_rota["caminho"],
                }

    return render_template(
        "rede.html",
        svg=montar_svg_rede(destaque, ordem, origem_svg, destino_svg),
        vertices=vertices,
        nomes=nomes,
        metricas=grafo_rede.obter_metricas(),
        arestas=grafo_rede.arestas(),
        adjacencia=grafo_rede.lista_adjacencia(),
        res_bfs=res_bfs, res_dfs=res_dfs, res_rota=res_rota, comparacao=comparacao,
        erros=erros,
        bfs_origem=bfs_origem, dfs_origem=dfs_origem, de=de, para=para, usar_cache=usar_cache,
        metricas_cache=cache_rotas.obter_metricas(),
    )


@app.route("/rede/arestas/salvar", methods=["POST"])
def salvar_aresta():
    """Cria uma conexão ou altera a latência de uma existente (invalida todo o cache de rotas)."""
    origem = request.form.get("origem", "").strip().upper()
    destino = request.form.get("destino", "").strip().upper()
    latencia = request.form.get("latencia", "").strip().replace(",", ".")
    try:
        acao = grafo_rede.adicionar_aresta(origem, destino, latencia)
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(url_for("rede"))

    persistir_rede()
    invalidadas = servico_rotas.invalidar_tudo()
    complemento = f" {invalidadas} rota(s) em cache foram invalidadas." if invalidadas else ""
    verbo = "criada" if acao == "criada" else "atualizada"
    flash(f"Conexão {origem} ↔ {destino} {verbo} ({latencia} ms).{complemento}", "success")
    return redirect(url_for("rede"))


@app.route("/rede/arestas/remover", methods=["POST"])
def remover_aresta():
    """Remove uma conexão da rede (invalida todo o cache de rotas)."""
    origem = request.form.get("origem", "").strip().upper()
    destino = request.form.get("destino", "").strip().upper()
    if grafo_rede.remover_aresta(origem, destino):
        persistir_rede()
        invalidadas = servico_rotas.invalidar_tudo()
        complemento = f" {invalidadas} rota(s) em cache foram invalidadas." if invalidadas else ""
        flash(f"Conexão {origem} ↔ {destino} removida.{complemento}", "warning")
    else:
        flash(f"Não existe conexão entre '{origem}' e '{destino}'.", "danger")
    return redirect(url_for("rede"))


# ==============================================================================
# ROTAS DA ETAPA 3 - DIFERENCIAL: CACHE LRU
# ==============================================================================

@app.route("/cache")
def cache():
    """Painel do Cache LRU: fila MRU -> LRU, métricas, eventos e resultado do benchmark."""
    ok, mensagem_validacao = cache_rotas.validar()
    return render_template(
        "cache.html",
        metricas=cache_rotas.obter_metricas(),
        servico=servico_rotas.obter_metricas(),
        entradas=cache_rotas.entradas(),
        nomes=nomes_paises(),
        valida=ok,
        mensagem_validacao=mensagem_validacao,
        benchmark=ultimo_benchmark,
        vertices=grafo_rede.vertices(),
    )


@app.route("/cache/configurar", methods=["POST"])
def configurar_cache():
    """Altera a capacidade (despejando os menos recentes se diminuir) e o TTL do cache."""
    try:
        capacidade = int(request.form.get("capacidade", ""))
        ttl = float(request.form.get("ttl", "0").replace(",", ".") or 0)
    except ValueError:
        flash("Informe números válidos para capacidade e TTL.", "danger")
        return redirect(url_for("cache"))
    if not 1 <= capacidade <= 1000 or not 0 <= ttl <= 86400:
        flash("A capacidade deve estar entre 1 e 1000 e o TTL entre 0 e 86400 s (0 = sem expiração).", "danger")
        return redirect(url_for("cache"))

    despejadas = cache_rotas.redimensionar(capacidade)
    cache_rotas.configurar_ttl(ttl or None)
    complemento = f" {len(despejadas)} entrada(s) menos recentes foram despejadas." if despejadas else ""
    flash(f"Cache configurado: capacidade {capacidade}, TTL {'desligado' if not ttl else f'{ttl:g} s'}.{complemento}", "success")
    return redirect(url_for("cache"))


@app.route("/cache/limpar", methods=["POST"])
def limpar_cache():
    removidas = servico_rotas.invalidar_tudo()
    flash(f"Cache esvaziado ({removidas} rota(s) removida(s)).", "warning")
    return redirect(url_for("cache"))


@app.route("/cache/benchmark", methods=["POST"])
def benchmark_cache():
    """Compara 'sempre Dijkstra' x 'Dijkstra + Cache LRU' (usa caches temporários, não altera o real)."""
    global ultimo_benchmark
    try:
        quantidade = int(request.form.get("quantidade", "2000"))
        semente = int(request.form.get("semente", "42"))
    except ValueError:
        flash("Informe números inteiros para a quantidade de consultas e a semente.", "danger")
        return redirect(url_for("cache"))
    if not 100 <= quantidade <= 20000:
        flash("A quantidade de consultas deve estar entre 100 e 20.000.", "danger")
        return redirect(url_for("cache"))

    resultado = executar_benchmark(grafo_rede, quantidade, semente)
    if "erro" in resultado:
        flash(resultado["erro"], "danger")
    else:
        ultimo_benchmark = resultado
        flash(f"Benchmark concluído com {quantidade} consultas (semente {semente}).", "success")
    return redirect(url_for("cache"))


@app.route("/design-system")
def design_system():
    """Exibe o catálogo visual de tokens, cores e componentes do GlobalSIM."""
    return render_template("design_system.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
