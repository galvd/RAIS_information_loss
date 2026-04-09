import pandas as pd
from shapely import wkt
import h3
import folium
import branca.colormap as cm
from branca.element import MacroElement, Template
import re

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
    return folium.Map(location=[centro_lat, centro_lon], zoom_start=11, tiles='CartoDB positron')

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