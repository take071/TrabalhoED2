"""
Aplicação Principal - GlobalSIM (Etapas 1 e 2)
Disciplina: Estruturas de Dados II - UNEB
Docente: Profa. Maria Inés Restovic
Equipe: Arthur Felipe, Lucas Vinicius, Raphael Lopes

Escopo da Etapa 1 (preservado integralmente):
- Tabela Hash própria para gerenciamento dos países atendidos.
- Consulta rápida de cobertura por código do país (ex: "BR", "IT") com mapa interativo Folium.
- CRUD completo de países atendidos com validação geográfica via Geopy e persistência em arquivos/paises.json.
- Painel de instrumentação básica da Tabela Hash (capacidade, colisões, fator de carga).
- Rotas de alteração de dados utilizando método POST (padrão Post/Redirect/Get).

Escopo da Etapa 2 (integrado à Etapa 1):
- Árvore B própria (estruturas/arvore_b.py) indexando ~1.000 clientes pelo ID.
- Cadastro, consulta por ID, listagem paginada e alteração de clientes.
- Associação de eSIM e pacote de serviço ao cliente.
- Persistência dos clientes em arquivos/clientes.json (pacotes em arquivos/pacotes.json).
- Consulta integrada: Árvore B (cliente) x Tabela Hash (cobertura do país de destino).
- Painel de instrumentação da Árvore B (altura, nós, divisões, caminho de busca).
"""

import os
import re
import json
import math
import random
import unicodedata
from flask import Flask, render_template, request, redirect, url_for, flash
import folium
from geopy.geocoders import Nominatim

from estruturas.tabela_hash import TabelaHash
from estruturas.arvore_b import ArvoreB

app = Flask(__name__)
app.secret_key = "globalsim-ed2-secret-key"

# Inicializa o buscador de coordenadas geográficas (Etapa 1)
geolocator = Nominatim(user_agent="globalsim_app")

# Caminhos de persistência (Etapas 1 e 2)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAISES_JSON_PATH = os.path.join(BASE_DIR, "arquivos", "paises.json")
CLIENTES_JSON_PATH = os.path.join(BASE_DIR, "arquivos", "clientes.json")
PACOTES_JSON_PATH = os.path.join(BASE_DIR, "arquivos", "pacotes.json")

# Instância da Tabela Hash em memória (Etapa 1)
tabela_paises = TabelaHash(capacidade_inicial=17)

# Instância da Árvore B em memória (Etapa 2): chave = ID do cliente; grau mínimo t = 3
# (cada nó guarda de 2 a 5 chaves, exceto a raiz, e possui até 6 filhos)
GRAU_MINIMO_ARVORE_B = 3
arvore_clientes = ArvoreB(grau_minimo=GRAU_MINIMO_ARVORE_B)

# Catálogo de pacotes de serviço (lista carregada de arquivos/pacotes.json)
pacotes = []

STATUS_VALIDOS = ("ativo", "inativo", "suspenso", "pendente")
CAMPOS_BUSCA_CLIENTES = ("id", "nome", "email", "esim")
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
    Persiste a Árvore B em arquivos/clientes.json, na ordem de inserção.
    Assim, ao reiniciar, a carga reconstrói exatamente a mesma árvore.
    A gravação é atômica (arquivo temporário + os.replace).
    """
    temporario = CLIENTES_JSON_PATH + ".tmp"
    try:
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(arvore_clientes.listar_em_ordem_de_insercao(), f, indent=2, ensure_ascii=False)
        os.replace(temporario, CLIENTES_JSON_PATH)
    except Exception as e:
        print(f"Erro ao persistir dados em {CLIENTES_JSON_PATH}: {e}")


# Carga inicial dos dados
carregar_dados()
carregar_pacotes()
carregar_clientes()


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


def normalizar_regiao(regiao: str) -> str:
    """
    Normaliza o nome de uma região geográfica para comparações seguras
    (remove acentos, ignora maiúsculas/minúsculas e trata plural 'Américas').
    """
    if not regiao:
        return ""
    base = unicodedata.normalize("NFKD", str(regiao).strip().lower())
    sem_acento = "".join(c for c in base if not unicodedata.combining(c))
    if sem_acento in ("america", "americas", "america do sul", "america do norte", "america central"):
        return "america"
    return sem_acento


def pacote_cobre_regiao(pacote: dict, regiao: str) -> bool:
    """Um pacote cobre o destino se for Global ou corresponder à mesma região do país."""
    regiao_pacote = normalizar_regiao(pacote.get("regiao", ""))
    regiao_destino = normalizar_regiao(regiao)
    if not regiao_pacote or not regiao_destino:
        return False
    return regiao_pacote == "global" or regiao_pacote == regiao_destino


# ==============================================================================
# ROTAS DA ETAPA 1 (PRESERVADAS E INTEGRADAS)
# ==============================================================================

@app.route("/")
def index():
    """Página inicial com mapa mundial Folium e visão geral das Etapas 1 e 2."""
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        width="100%",
        height="100%",
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
    )

    paises_cadastrados = tabela_paises.listar_todos()
    for p in paises_cadastrados:
        lat = p.get("lat")
        lon = p.get("lon")
        if lat and lon:
            texto_popup = (
                f"<b>{p['pais']}</b> ({p['codigo']})<br>"
                f"<small>{p['operadora']}</small><br>"
                f"<span style='color: green;'>{p.get('tecnologia', '5G')}</span>"
            )
            folium.Marker(location=[lat, lon], popup=texto_popup).add_to(m)

    mapa_html = m._repr_html_()

    return render_template(
        "index.html",
        metricas=tabela_paises.obter_metricas(),
        metricas_arvore=arvore_clientes.obter_metricas(),
        mapa=mapa_html,
    )


@app.route("/cobertura", methods=["GET", "POST"])
def cobertura():
    """Consulta rápida de cobertura por código ISO na Tabela Hash com mapa Folium."""
    resultado = None
    codigo_buscado = ""
    consultado = False
    mapa_html = None

    if request.method == "POST":
        consultado = True
        codigo_buscado = request.form.get("codigo", "").strip().upper()

        if codigo_buscado:
            resultado = tabela_paises.buscar(codigo_buscado)

            if resultado:
                lat = resultado.get("lat")
                lon = resultado.get("lon")

                if not lat or not lon:
                    try:
                        loc = geolocator.geocode(resultado["pais"])
                        lat = loc.latitude if loc else 0
                        lon = loc.longitude if loc else 0
                    except Exception:
                        lat, lon = 0, 0

                if lat and lon:
                    m = folium.Map(
                        location=[lat, lon],
                        zoom_start=4,
                        width="100%",
                        height="100%",
                        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
                        attr="Esri",
                    )
                    texto_popup = f"<b>{resultado['pais']}</b> ({resultado['codigo']})<br><small>{resultado['operadora']}</small>"
                    folium.Marker(location=[lat, lon], popup=texto_popup).add_to(m)
                    mapa_html = m._repr_html_()

    return render_template(
        "cobertura.html",
        resultado=resultado,
        codigo=codigo_buscado,
        consultado=consultado,
        mapa=mapa_html,
    )


@app.route("/paises")
def paises():
    """Listagem de todos os países atendidos cadastrados na Tabela Hash."""
    lista_paises = tabela_paises.listar_todos()
    return render_template(
        "paises.html",
        paises=lista_paises,
        form_data={},
        cadastro_erro=False,
    )


@app.route("/paises/cadastrar", methods=["POST"])
def cadastrar_pais():
    """
    Cadastra um novo país na Tabela Hash, busca coordenadas via Geopy e persiste no JSON.
    """
    codigo = request.form.get("codigo", "").strip().upper()
    pais = request.form.get("pais", "").strip()
    regiao = request.form.get("regiao", "").strip()
    operadora = request.form.get("operadora", "").strip()
    tecnologia = request.form.get("tecnologia", "5G").strip().upper()

    if not codigo or not pais or not regiao or not operadora or not tecnologia:
        flash("Todos os campos são obrigatórios para o cadastro!", "danger")
        return redirect(url_for("paises"))

    localizacao = geolocator.geocode(pais, featuretype="country")
    if localizacao is None:
        return render_template(
            "paises.html",
            paises=tabela_paises.listar_todos(),
            cadastro_erro=True,
            form_data={
                "codigo": codigo,
                "pais": pais,
                "regiao": regiao,
                "operadora": operadora,
                "tecnologia": tecnologia,
            },
        )

    lat = localizacao.latitude
    lon = localizacao.longitude

    existente = tabela_paises.buscar(codigo)
    novo_registro = {
        "codigo": codigo,
        "pais": pais,
        "regiao": regiao,
        "operadora": operadora,
        "tecnologia": tecnologia,
        "lat": lat,
        "lon": lon,
    }

    tabela_paises.inserir(codigo, novo_registro)
    persistir_dados()

    if existente:
        flash(f"O país com código '{codigo}' já existia e foi atualizado com sucesso!", "info")
    else:
        flash(f"País '{pais}' ({codigo}) cadastrado com sucesso!", "success")

    return redirect(url_for("paises"))


@app.route("/paises/<codigo>/editar", methods=["POST"])
def editar_pais(codigo):
    """
    Atualiza os dados de um país existente na Tabela Hash e persiste no JSON,
    preservando as coordenadas geográficas já armazenadas.
    """
    codigo = codigo.strip().upper()
    pais = request.form.get("pais", "").strip()
    regiao = request.form.get("regiao", "").strip()
    operadora = request.form.get("operadora", "").strip()
    tecnologia = request.form.get("tecnologia", "5G").strip().upper()

    if not pais or not regiao or not operadora or not tecnologia:
        flash("Todos os campos são obrigatórios para a edição!", "danger")
        return redirect(url_for("paises"))

    existente = tabela_paises.buscar(codigo)
    lat = existente.get("lat") if existente else 0
    lon = existente.get("lon") if existente else 0

    dados_atualizados = {
        "codigo": codigo,
        "pais": pais,
        "regiao": regiao,
        "operadora": operadora,
        "tecnologia": tecnologia,
        "lat": lat,
        "lon": lon,
    }

    tabela_paises.inserir(codigo, dados_atualizados)
    persistir_dados()
    flash(f"Dados do país {codigo} ({pais}) atualizados com sucesso!", "success")
    return redirect(url_for("paises"))


@app.route("/paises/<codigo>/excluir", methods=["POST"])
def excluir_pais(codigo):
    """Remove um país da Tabela Hash e atualiza o arquivo JSON."""
    codigo = codigo.strip().upper()
    removido = tabela_paises.remover(codigo)

    if removido:
        persistir_dados()
        flash(f"País '{codigo}' removido com sucesso!", "warning")
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
    - ?id=...: consulta exata por ID diretamente na Árvore B em O(log n) (com caminho percorrido).
    - ?campo=id|nome|email|esim&q=...: filtro seletivo (parcial) isolado ao campo escolhido
      sobre o percurso em ordem da Árvore B.
    - ?status=...&pagina=...: filtro de status e paginação da listagem.
    """
    id_buscado = request.args.get("id", "").strip()
    campo = request.args.get("campo", "id").strip().lower()
    if campo not in CAMPOS_BUSCA_CLIENTES:
        campo = "id"

    termo_bruto = request.args.get("q", "").strip()
    termo = termo_bruto.lower()
    status = request.args.get("status", "").strip().lower()

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

    lista = arvore_clientes.listar_todos()
    if termo:
        if campo == "id":
            lista = [c for c in lista if termo in str(c["id"])]
        elif campo == "nome":
            lista = [c for c in lista if termo in c["nome"].lower()]
        elif campo == "email":
            lista = [c for c in lista if termo in c["email"].lower()]
        elif campo == "esim":
            lista = [c for c in lista if termo in (c.get("esim") or "").lower()]

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
        q=termo_bruto,
        campo_filtro=campo,
        status_filtro=status,
        status_validos=STATUS_VALIDOS,
        pacotes=pacotes,
        nomes_pacotes={p["codigo"]: p["nome"] for p in pacotes},
        metricas_arvore=arvore_clientes.obter_metricas(),
    )


@app.route("/clientes/cadastrar", methods=["POST"])
def cadastrar_cliente():
    """
    Cadastra um novo cliente na Árvore B e persiste no JSON (padrão Post/Redirect/Get).
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
    """Altera nome, e-mail e status de um cliente existente na Árvore B."""
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
    Associa um eSIM e um pacote de serviço ao cliente na Árvore B e persiste no JSON.
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

@app.route("/consulta", methods=["GET", "POST"])
def consulta():
    """
    Consulta integrada cliente x país de destino:
      1. Árvore B:     buscar(id_cliente) -> cliente, eSIM, pacote e status
      2. Tabela Hash:  buscar(destino)    -> cobertura, operadora e tecnologia
      3. Pacotes:      verifica se o pacote do cliente cobre a região do destino
    """
    origem = request.form if request.method == "POST" else request.args
    cliente_raw = origem.get("cliente", "").strip()
    destino_raw = origem.get("destino", "").strip().upper()
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

        resultado = {
            "cliente_id": cliente_id,
            "cliente": cliente,
            "arvore": instrumentacao_arvore,
            "destino": destino_raw,
            "pais": pais,
            "pacote": pacote,
            "compativel": compativel,
            "pendencias": pendencias,
            "apto": not pendencias,
        }

    return render_template(
        "consulta.html",
        resultado=resultado,
        consultado=consultado,
        cliente_valor=cliente_raw,
        destino_valor=destino_raw,
        paises=sorted(tabela_paises.listar_todos(), key=lambda p: p["pais"]),
    )


@app.route("/design-system")
def design_system():
    """Exibe o catálogo visual de tokens, cores e componentes do GlobalSIM."""
    return render_template("design_system.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
