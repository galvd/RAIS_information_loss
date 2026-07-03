import json

# Municípios da Região Metropolitana da Grande Vitória (limiar de 50 vínculos)
RMGV = {'Vitória', 'Vila Velha', 'Serra', 'Cariacica', 'Viana', 'Guarapari', 'Fundão'}
LIMIAR_RMGV = 50
LIMIAR_INTERIOR = 20


def gerar_dados_tabela(df):
    """Agrega por município + classe CNAE. Retorna dict {municipio: [top10], 'Todos': [top10]}."""
    df2 = df.dropna(subset=['media_salarial_da_classe', 'media_vinculos_da_classe']).copy()

    df2['cnae_classe_num'] = df2['cnae_classe_num'].apply(
        lambda x: str(x).split('.')[0].zfill(5)
    )
    df2['cnae_classe_desc'] = df2['cnae_classe_desc'].fillna('Indefinido').astype(str)
    df2['vinc_row'] = df2['media_vinculos_da_classe'] * df2['total_cnpjs_no_cep']

    g = df2.groupby(
        ['id_municipio_nome', 'cnae_classe_num', 'cnae_classe_desc'], as_index=False
    ).agg(
        salario=('media_salarial_da_classe', 'first'),
        vinculos=('vinc_row', 'sum')
    )

    # Corte do 0.5% superior (remoção de outliers de salário)
    limite_sup_sal = g['salario'].quantile(0.995)
    g = g[g['salario'] <= limite_sup_sal].copy()

    resultado = {}

    # Top 10 por município: limiar de vínculos varia por porte (RMGV=50, interior=20)
    g['limiar'] = g['id_municipio_nome'].apply(
        lambda mun: LIMIAR_RMGV if mun in RMGV else LIMIAR_INTERIOR
    )
    g_mun = g[g['vinculos'] >= g['limiar']]
    for mun, sub in g_mun.groupby('id_municipio_nome'):
        top = sub.sort_values('salario', ascending=False).head(10)
        resultado[mun] = [
            {
                'classe': r['cnae_classe_num'],
                'desc': r['cnae_classe_desc'],
                'salario': round(float(r['salario']), 2),
                'vinculos': float(r['vinculos'])
            }
            for _, r in top.iterrows()
        ]

    # Nível estadual: agrega a classe primeiro (sem filtro municipal),
    # média ponderada por vínculos, e só então aplica o corte de 50.
    g['ws'] = g['salario'] * g['vinculos']
    est = g.groupby(['cnae_classe_num', 'cnae_classe_desc'], as_index=False).agg(
        ws=('ws', 'sum'),
        vinculos=('vinculos', 'sum')
    )
    est = est[est['vinculos'] >= LIMIAR_RMGV].copy()
    est['salario'] = est['ws'] / est['vinculos']
    top_est = est.sort_values('salario', ascending=False).head(10)
    resultado['Todos'] = [
        {
            'classe': r['cnae_classe_num'],
            'desc': r['cnae_classe_desc'],
            'salario': round(float(r['salario']), 2),
            'vinculos': float(r['vinculos'])
        }
        for _, r in top_est.iterrows()
    ]

    return resultado


def montar_options(dados):
    municipios = sorted([m for m in dados.keys() if m != 'Todos'])
    opts = ["<option value='Todos'>Todos os Municípios</option>"]
    opts += [f"<option value=\"{m}\">{m}</option>" for m in municipios]
    return "".join(opts)


def gerar_tabela_salarios(df):
    """Retorna (dados_json, mun_options) prontos para injeção no HTML."""
    dados = gerar_dados_tabela(df)
    return json.dumps(dados, ensure_ascii=False), montar_options(dados)