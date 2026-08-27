import json
import os
import re
from pathlib import Path

import pandas as pd
from shapely import wkt
import h3
import folium
import branca.colormap as cm
from branca.element import MacroElement, Template

# ==========================================
# BASEMAP DA CARTO (exige chave desde 2025)
# ==========================================
# O folium tem o atalho tiles='CartoDB positron', que aponta para o endpoint
# antigo e SEM chave. Desde 2025 a CARTO carimba esses tiles com a marca d'água
# "API KEY REQUIRED" — o mapa continua funcionando, só fica ilegível. Por isso o
# atalho foi trocado por uma TileLayer explícita com a chave.
#
# A chave é gratuita (https://carto.com/basemaps/apikey), 5 milhões de tiles por
# mês, uso não comercial. ATENÇÃO: ela NÃO é restrita por domínio — confirmado
# com o suporte. O domínio pedido no formulário é registro interno deles. Como a
# chave fica visível no HTML publicado, qualquer um pode copiá-la e gastar a
# cota. Não há defesa técnica; a única saída é notar consumo anormal e pedir a
# rotação. Não escrever em lugar nenhum que o domínio protege isto.
#
# A atribuição CARTO + OpenStreetMap é obrigatória pelos termos da chave.
CARTO_TILES = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"
CARTO_ATTR = ('&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
              '&copy; <a href="https://carto.com/attributions">CARTO</a>')

# A chave é alfanumérica com underscore/hífen. Qualquer outra coisa é valor
# colado errado — tipicamente a URL de exemplo do e-mail inteira.
_KEY_OK = re.compile(r"^[A-Za-z0-9_-]{8,}$")
_KEY_CACHE = None


def _limpa_key(v):
    """Extrai a chave de um valor colado, tolerando o erro mais comum.

    O e-mail da CARTO entrega a chave dentro de uma URL de exemplo
    (`https://.../{z}/{x}/{y}.png?key=SUA_CHAVE`), e é natural copiar a linha
    inteira para o config.json. Quando isso acontece o tile volta com marca
    d'água e nada no log denuncia — daí a limpeza aqui.
    """
    v = str(v or "").strip().strip('"\'')
    if "key=" in v:                      # colou a URL de exemplo inteira
        v = v.split("key=", 1)[1]
    return v.split("&", 1)[0].split("#", 1)[0].strip()


def carto_key():
    """Chave do basemap. Ordem: variável de ambiente CARTO_KEY, depois o
    config.json do projeto (procurado subindo a partir deste arquivo).

    Procura subindo em vez de usar caminho fixo porque os módulos ficam em
    pyfiles/ e os scripts são chamados da raiz: um caminho relativo quebraria
    dependendo de onde o python foi invocado.
    """
    global _KEY_CACHE
    if _KEY_CACHE is not None:
        return _KEY_CACHE
    k = _limpa_key(os.environ.get("CARTO_KEY", ""))
    if not k:
        base = Path(__file__).resolve()
        candidatos = []
        for pai in [base.parent] + list(base.parents):
            candidatos += [pai / "settings" / "config.json", pai / "config.json"]
        for c in candidatos:
            try:
                if c.is_file():
                    k = _limpa_key(json.loads(c.read_text(encoding="utf-8")).get("carto_key", ""))
                    if k:
                        print(f"[Basemap] chave do CARTO lida de {c}")
                        break
            except Exception as e:
                print(f"[Basemap] não consegui ler {c} ({e}); seguindo.")
    if k and not _KEY_OK.match(k):
        print("[Basemap] AVISO: a chave tem caracteres estranhos (barra, dois-pontos, "
              "espaço). O campo \"carto_key\" deve conter SÓ a chave, não a URL de "
              "exemplo do e-mail. Os mapas vão sair com marca d'água.")
    if not k:
        print("[Basemap] AVISO: sem chave do CARTO. Os mapas vão sair com a marca "
              "d'água 'API KEY REQUIRED'. Peça a chave gratuita em "
              "https://carto.com/basemaps/apikey e grave em settings/config.json "
              "como \"carto_key\" (ou exporte CARTO_KEY).")
    _KEY_CACHE = k
    return k


def tiles_carto():
    """TileLayer do Positron com a chave, pronta para .add_to(mapa)."""
    key = carto_key()
    url = CARTO_TILES + ("?key=" + key if key else "")
    if key:
        print(f"[Basemap] CARTO Positron com chave ({len(key)} caracteres, "
              f"{key[:6]}…{key[-4:]}).")
    return folium.TileLayer(
        tiles=url, attr=CARTO_ATTR, name="CartoDB Positron",
        subdomains="abcd", max_zoom=20, control=False, overlay=False,
    )

# ==========================================
# TEMPLATES E CLASSES
# ==========================================

TEMPLATE_JS_FILTROS = """
{% macro html(this, kwargs) %}
<!DOCTYPE html>
<html>
<head>
    <style>
        #mapa-controles {
            position: absolute;
            bottom: 30px;
            left: 30px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            z-index: 9999;
            font-family: Arial, sans-serif;
            font-size: 14px;
        }
        .filtro-linha { margin-bottom: 10px; }
        .filtro-linha select { width: 100%; padding: 5px; margin-top: 5px; }
    </style>
</head>
<body>
    <div id="mapa-controles">
        <h4>Filtros Interativos</h4>
        <div class="filtro-linha">
            <label for="filtro-mun"><b>Município:</b></label><br>
            <select id="filtro-mun" onchange="aplicarFiltros()">
                <option value="Todos">Todos os Municípios</option>
                {{ this.mun_opts }}
            </select>
        </div>
        <div class="filtro-linha">
            <label for="filtro-cnae"><b>Grupo CNAE:</b></label><br>
            <select id="filtro-cnae" onchange="aplicarFiltros()">
                <option value="Todos">Todos os Grupos</option>
                {{ this.cnae_opts }}
            </select>
        </div>
    </div>
    <script>
        function aplicarFiltros() {
            var mun_selecionado = document.getElementById('filtro-mun').value;
            var cnae_selecionado = document.getElementById('filtro-cnae').value;
            var caminhos = document.querySelectorAll('path.hex-polygon');
            
            caminhos.forEach(function(path) {
                var mostra_mun = (mun_selecionado === 'Todos') || path.classList.contains(mun_selecionado);
                var mostra_cnae = (cnae_selecionado === 'Todos') || path.classList.contains(cnae_selecionado);
                
                if (mostra_mun && mostra_cnae) {
                    path.style.display = '';
                } else {
                    path.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
{% endmacro %}
"""

class FiltrosJS(MacroElement):
    def __init__(self, template_str, mun_opts, cnae_opts):
        super().__init__()
        self._template = Template(template_str)
        self.mun_opts = mun_opts
        self.cnae_opts = cnae_opts

# ==========================================
# FUNÇÕES DE PROCESSAMENTO E FORMATAÇÃO
# ==========================================

def sanitize(text):
    return re.sub(r'\W+', '_', str(text))

def get_hex_polygon(hex_id):
    boundary = h3.cell_to_boundary(hex_id)
    coords = [[lon, lat] for lat, lon in boundary]
    coords.append(coords[0])
    return {"type": "Polygon", "coordinates": [coords]}

def preparar_dados_base(df, interativo=False):
    df_base = df.dropna(subset=['centroide_cep', 'media_salarial_da_classe', 'media_vinculos_da_classe']).copy()
    df_base['geometry'] = df_base['centroide_cep'].apply(wkt.loads)
    df_base['lat'] = df_base['geometry'].apply(lambda p: p.y)
    df_base['lon'] = df_base['geometry'].apply(lambda p: p.x)

    # municipios_rmgv = ['Vitória', 'Vila Velha', 'Serra', 'Cariacica', 'Viana', 'Guarapari', 'Fundão']
    # df_base = df_base[df_base['id_municipio_nome'].isin(municipios_rmgv)].copy()

    if interativo:
        df_base['cnae_label'] = df_base['cnae_subclasse'].astype(str) + ' - ' + df_base['cnae_subclasse_desc'].fillna('Indefinido').astype(str)

    RESOLUTION = 9
    df_base['hex_id'] = df_base.apply(lambda row: h3.latlng_to_cell(row['lat'], row['lon'], RESOLUTION), axis=1)
    df_base['vinculos_totais'] = df_base['media_vinculos_da_classe'] * df_base['total_cnpjs_no_cep']
    df_base['massa_salarial'] = df_base['media_salarial_da_classe'] * df_base['vinculos_totais']
    
    return df_base

def iniciar_mapa(df_base):
    centro_lat = df_base['lat'].mean()
    centro_lon = df_base['lon'].mean()
    # tiles=None: o basemap entra como TileLayer explícita (com chave), não pelo
    # atalho 'CartoDB positron' do folium, que aponta para o endpoint sem chave.
    m = folium.Map(location=[centro_lat, centro_lon], zoom_start=11, tiles=None)
    tiles_carto().add_to(m)
    return m

def criar_colormap(series, legend_caption, colors):
    min_val = series.quantile(0.02)
    max_val = series.quantile(0.98)
    if min_val == max_val:
        min_val, max_val = min_val * 0.9, max_val * 1.1
        if min_val == 0:
            max_val = 1
            
    colormap = cm.LinearColormap(colors=colors, vmin=min_val, vmax=max_val)
    colormap.caption = legend_caption
    return colormap, min_val, max_val

def injetar_css_legenda(m):
    estilo_legenda = """
    <style>
        .legend {
            transform: scale(1.4); 
            transform-origin: top right; 
            margin-top: 40px !important; 
            margin-right: 20px !important; 
        }   
    </style>
    """
    m.get_root().header.add_child(folium.Element(estilo_legenda))