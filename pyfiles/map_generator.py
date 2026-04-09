import os
import folium
from pyfiles.map_utils import (
                                preparar_dados_base, 
                                get_hex_polygon, 
                                iniciar_mapa, 
                                criar_colormap, 
                                injetar_css_legenda, 
                                sanitize, 
                                FiltrosJS, 
                                TEMPLATE_JS_FILTROS
)


def gerar_mapa_estatico_salarios(df, pasta_destino):
    df_base = preparar_dados_base(df, interativo=False)

    df_hex = df_base.groupby('hex_id').agg(
        soma_massa=('massa_salarial', 'sum'),
        soma_vinculos=('vinculos_totais', 'sum')
    ).reset_index()

    df_hex = df_hex[df_hex['soma_vinculos'] > 0].copy()
    df_hex['media_salarial_ponderada'] = df_hex['soma_massa'] / df_hex['soma_vinculos']
    df_hex['geometry'] = df_hex['hex_id'].apply(get_hex_polygon)

    m = iniciar_mapa(df_base)
    cores = ['#fef0d9', '#fdcc8a', '#fc8d59', '#e34a33', '#b30000']
    colormap, min_val, max_val = criar_colormap(df_hex['media_salarial_ponderada'], 'Média Salarial Ponderada (R$) - Normalizada 40h', cores)
    colormap.add_to(m)
    injetar_css_legenda(m)

    for _, row in df_hex.iterrows():
        val = max(min(row['media_salarial_ponderada'], max_val), min_val)
        folium.GeoJson(
            {"type": "Feature", "geometry": row['geometry']},
            style_function=lambda feature, color=colormap(val): {
                'fillColor': color, 'color': 'black', 'weight': 0.5, 'fillOpacity': 0.7
            },
            tooltip=folium.Tooltip(
                f"<b>Salário Médio Real:</b> R$ {row['media_salarial_ponderada']:,.2f}<br>"
                f"<b>Vínculos Estimados:</b> {row['soma_vinculos']:,.0f}"
            )
        ).add_to(m)

    caminho_html = os.path.join(pasta_destino, 'mapa_salarios_estatico.html')
    m.save(caminho_html)


def gerar_mapa_estatico_vinculos(df, pasta_destino):
    df_base = preparar_dados_base(df, interativo=False)

    df_hex = df_base.groupby('hex_id').agg(
        total_vinculos=('vinculos_totais', 'sum')
    ).reset_index()

    df_hex = df_hex[df_hex['total_vinculos'] > 0].copy()
    df_hex['geometry'] = df_hex['hex_id'].apply(get_hex_polygon)

    m = iniciar_mapa(df_base)
    cores = ['#eff3ff', '#bdd7e7', '#6baed6', '#3182bd', '#08519c']
    colormap, min_val, max_val = criar_colormap(df_hex['total_vinculos'], 'Total de Vínculos Estimados', cores)
    colormap.add_to(m)
    injetar_css_legenda(m)

    for _, row in df_hex.iterrows():
        val = max(min(row['total_vinculos'], max_val), min_val)
        folium.GeoJson(
            {"type": "Feature", "geometry": row['geometry']},
            style_function=lambda feature, color=colormap(val): {
                'fillColor': color, 'color': 'black', 'weight': 0.5, 'fillOpacity': 0.7
            },
            tooltip=folium.Tooltip(
                f"<b>Vínculos Estimados:</b> {row['total_vinculos']:,.0f}"
            )
        ).add_to(m)

    caminho_html = os.path.join(pasta_destino, 'mapa_vinculos_estatico.html')
    m.save(caminho_html)


def gerar_mapa_estatico_cnpjs(df, pasta_destino):
    df_base = preparar_dados_base(df, interativo=False)

    df_hex = df_base.groupby('hex_id').agg(
        total_empresas=('total_cnpjs_no_cep', 'sum')
    ).reset_index()

    df_hex = df_hex[df_hex['total_empresas'] > 0].copy()
    df_hex['geometry'] = df_hex['hex_id'].apply(get_hex_polygon)

    m = iniciar_mapa(df_base)
    cores = ['#f2f0f7', '#cbc9e2', '#9e9ac8', '#756bb1', '#54278f']
    colormap, min_val, max_val = criar_colormap(df_hex['total_empresas'], 'Total de Empresas (CNPJs)', cores)
    colormap.add_to(m)
    injetar_css_legenda(m)

    for _, row in df_hex.iterrows():
        val = max(min(row['total_empresas'], max_val), min_val)
        folium.GeoJson(
            {"type": "Feature", "geometry": row['geometry']},
            style_function=lambda feature, color=colormap(val): {
                'fillColor': color, 'color': 'black', 'weight': 0.5, 'fillOpacity': 0.7
            },
            tooltip=folium.Tooltip(
                f"<b>Empresas (CNPJs):</b> {row['total_empresas']:,.0f}"
            )
        ).add_to(m)

    caminho_html = os.path.join(pasta_destino, 'mapa_cnpjs_estatico.html')
    m.save(caminho_html)



def gerar_mapa_interativo_salarios(df, pasta_destino):
    df_base = preparar_dados_base(df, interativo=True)

    df_hex = df_base.groupby(['hex_id', 'id_municipio_nome', 'cnae_label']).agg(
        soma_massa=('massa_salarial', 'sum'),
        soma_vinculos=('vinculos_totais', 'sum')
    ).reset_index()

    df_hex = df_hex[df_hex['soma_vinculos'] > 0].copy()
    df_hex['media_salarial_ponderada'] = df_hex['soma_massa'] / df_hex['soma_vinculos']
    df_hex['geometry'] = df_hex['hex_id'].apply(get_hex_polygon)

    m = iniciar_mapa(df_base)
    cores = ['#fef0d9', '#fdcc8a', '#fc8d59', '#e34a33', '#b30000']
    colormap, min_val, max_val = criar_colormap(df_hex['media_salarial_ponderada'], 'Média Salarial Ponderada (R$)', cores)
    colormap.add_to(m)
    injetar_css_legenda(m)

    hex_group = folium.FeatureGroup(name="Hexágonos Salariais").add_to(m)

    for _, row in df_hex.iterrows():
        val = max(min(row['media_salarial_ponderada'], max_val), min_val)
        mun_cls = "mun_" + sanitize(row['id_municipio_nome'])
        cnae_cls = "cnae_" + sanitize(row['cnae_label'])
        
        folium.GeoJson(
            {"type": "Feature", "geometry": row['geometry']},
            style_function=lambda feature, color=colormap(val), c1=mun_cls, c2=cnae_cls: {
                'fillColor': color, 'color': 'black', 'weight': 0.5, 'fillOpacity': 0.7,
                'className': f'hex-polygon {c1} {c2}'
            },
            tooltip=folium.Tooltip(
                f"<b>Município:</b> {row['id_municipio_nome']}<br>"
                f"<b>Salário Médio Real:</b> R$ {row['media_salarial_ponderada']:,.2f}<br>"
                f"<b>Vínculos Estimados:</b> {row['soma_vinculos']:,.0f}"
            )
        ).add_to(hex_group)

    opcoes_mun = sorted(df_base['id_municipio_nome'].unique().tolist())
    opcoes_cnae = sorted(df_base['cnae_label'].unique().tolist())

    html_mun_options = "".join([f"<option value='mun_{sanitize(m)}'>{m}</option>" for m in opcoes_mun])
    html_cnae_options = "".join([f"<option value='cnae_{sanitize(c)}'>{c}</option>" for c in opcoes_cnae])

    painel_filtros = FiltrosJS(TEMPLATE_JS_FILTROS, html_mun_options, html_cnae_options)
    m.get_root().add_child(painel_filtros)

    caminho_html = os.path.join(pasta_destino, 'mapa_salarios_interativo.html')
    m.save(caminho_html)