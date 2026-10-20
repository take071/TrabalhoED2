"""
Aplicação Principal - GlobalSIM (Etapa 1)
Disciplina: Estruturas de Dados II - UNEB
Docente: Profa. Maria Inés Restovic
Equipe: Arthur Felipe, Lucas Vinicius, Raphael Lopes

Escopo da Etapa 1:
- Tabela Hash própria para gerenciamento dos países atendidos.
- Consulta rápida de cobertura por código do país (ex: "BR", "IT").
- CRUD completo de países atendidos com persistência em arquivos/paises.json.
- Painel de instrumentação básica da estrutura (capacidade, colisões, fator de carga).
- Rotas de alteração de dados utilizando método POST (padrão Post/Redirect/Get).
"""

import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash
import folium
from geopy.geocoders import Nominatim

# Inicializa o buscador de coordenadas
geolocator = Nominatim(user_agent="globalsim_app")

from estruturas.tabela_hash import TabelaHash

app = Flask(__name__)
app.secret_key = "globalsim-ed2-secret-key"

# Caminho para o arquivo de persistência dos países (Etapa 1)
PAISES_JSON_PATH = os.path.join(os.path.dirname(__file__), "arquivos", "paises.json")

# Instância da Tabela Hash em memória
tabela_paises = TabelaHash(capacidade_inicial=17)


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


# Carga inicial dos dados
carregar_dados()


# ==============================================================================
# ROTAS DA ETAPA 1
# ==============================================================================


@app.route("/")
def index():
    # Inicialização do mapa mundial centrado
    m = folium.Map(
        location=[20, 0], 
        zoom_start=2,
        width='100%', 
        height='100%',
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri'
    )

    # Marcações dinâmicas a partir da Tabela Hash em memória
    paises_cadastrados = tabela_paises.listar_todos()
    for p in paises_cadastrados:
        lat = p.get('lat')
        lon = p.get('lon')
        
        # Só adiciona o marcador se as coordenadas existirem
        if lat and lon:
            texto_popup = f"<b>{p['pais']}</b> ({p['codigo']})<br><small>{p['operadora']}</small><br><span style='color: green;'>{p.get('tecnologia', '5G')}</span>"
            folium.Marker(
                location=[lat, lon],
                popup=texto_popup
            ).add_to(m)

    # Extrai o HTML do mapa para injetar no Flask
    mapa_html = m._repr_html_()

    return render_template("index.html", metricas=tabela_paises.obter_metricas(), mapa=mapa_html)

@app.route("/cobertura", methods=["GET", "POST"])
def cobertura():
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
                lat = resultado.get('lat')
                lon = resultado.get('lon')
                
                # Se o país for antigo e não tiver lat/lon, procuramos agora!
                if not lat or not lon:
                    loc = geolocator.geocode(resultado['pais'])
                    lat = loc.latitude if loc else 0
                    lon = loc.longitude if loc else 0
                
                if lat and lon:
                    m = folium.Map(
                        location=[lat, lon], 
                        zoom_start=4,
                        width='100%', 
                        height='100%',
                        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
                        attr='Esri'
                    )
                    
                    texto_popup = f"<b>{resultado['pais']}</b> ({resultado['codigo']})<br><small>{resultado['operadora']}</small>"
                    
                    folium.Marker(
                        location=[lat, lon],
                        popup=texto_popup
                    ).add_to(m)
                    
                    mapa_html = m._repr_html_()

    return render_template(
        "cobertura.html",
        resultado=resultado,
        codigo=codigo_buscado,
        consultado=consultado,
        mapa=mapa_html
    )
@app.route("/paises")
def paises():
    """Listagem de todos os países atendidos cadastrados na Tabela Hash."""
    lista_paises = tabela_paises.listar_todos()
    return render_template("paises.html", paises=lista_paises)


# Inicializa o buscador de coordenadas
geolocator = Nominatim(user_agent="globalsim_app")

@app.route("/paises/cadastrar", methods=["POST"])
def cadastrar_pais():
    """
    Cadastra um novo país na Tabela Hash, busca coordenadas via Geopy e persiste no JSON.
    """
    # Pegando dados e garantindo formatação correta (maiúsculas e sem espaços extras)
    codigo = request.form.get("codigo", "").strip().upper()
    pais = request.form.get("pais", "").strip()
    regiao = request.form.get("regiao", "").strip()
    operadora = request.form.get("operadora", "").strip()
    tecnologia = request.form.get("tecnologia", "5G").strip().upper()

    # Validação de segurança
    if not codigo or not pais or not regiao or not operadora or not tecnologia:
        flash("Todos os campos são obrigatórios para o cadastro!", "danger")
        return redirect(url_for("paises"))

    # 1. Busca a latitude e longitude usando o nome do país
    localizacao = geolocator.geocode(pais)
    lat = localizacao.latitude if localizacao else 0
    lon = localizacao.longitude if localizacao else 0

    # Verifica se já existia para dar o aviso correto (inserção ou atualização)
    existente = tabela_paises.buscar(codigo)

    # 2. Cria o dicionário adicionando lat e lon
    novo_registro = {
        "codigo": codigo,
        "pais": pais,
        "regiao": regiao,
        "operadora": operadora,
        "tecnologia": tecnologia,
        "lat": lat,
        "lon": lon
    }

    # 3. Insere na sua Tabela Hash e salva no JSON
    tabela_paises.inserir(codigo, novo_registro)
    persistir_dados()
    
    # Feedback visual para o usuário
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
        "lon": lon
    }

    tabela_paises.inserir(codigo, dados_atualizados)
    persistir_dados()
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


@app.route("/design-system")
def design_system():
    """Exibe o catálogo visual de tokens, cores e componentes do GlobalSIM."""
    return render_template("design_system.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
