import json

# Municípios da Região Metropolitana da Grande Vitória (limiar de 50 vínculos)
RMGV = {'Vitória', 'Vila Velha', 'Serra', 'Cariacica', 'Viana', 'Guarapari', 'Fundão'}
LIMIAR_RMGV = 50
LIMIAR_INTERIOR = 20

# Microrregiões de Planejamento do ES (IJSN / Lei 9.768, atualizada pela 11.174/2020)
REGIOES = {
    'Metropolitana': ['Fundão', 'Serra', 'Cariacica', 'Viana', 'Vitória', 'Vila Velha', 'Guarapari'],
    'Central Serrana': ['Itaguaçu', 'Itarana', 'Santa Teresa', 'Santa Maria de Jetibá', 'Santa Leopoldina'],
    'Sudoeste Serrana': ['Laranja da Terra', 'Afonso Cláudio', 'Brejetuba', 'Conceição do Castelo', 'Venda Nova do Imigrante', 'Domingos Martins', 'Marechal Floriano'],
    'Litoral Sul': ['Alfredo Chaves', 'Anchieta', 'Iconha', 'Piúma', 'Rio Novo do Sul', 'Itapemirim', 'Marataízes', 'Presidente Kennedy'],
    'Central Sul': ['Castelo', 'Vargem Alta', 'Cachoeiro de Itapemirim', 'Muqui', 'Atilio Vivacqua', 'Mimoso do Sul', 'Apiacá'],
    'Caparaó': ['Ibatiba', 'Irupi', 'Iúna', 'Ibitirama', 'Muniz Freire', 'Divino de São Lourenço', 'Jerônimo Monteiro', 'Alegre', 'Dores do Rio Preto', 'Guaçuí', 'São José do Calçado', 'Bom Jesus do Norte'],
    'Rio Doce': ['Aracruz', 'Ibiraçu', 'João Neiva', 'Linhares', 'Rio Bananal', 'Sooretama'],
    'Centro-Oeste': ['Baixo Guandu', 'São Roque do Canaã', 'Colatina', 'Marilândia', 'Pancas', 'Governador Lindenberg', 'São Domingos do Norte', 'Alto Rio Novo', 'Vila Valério', 'São Gabriel da Palha'],
    'Nordeste': ['Jaguaré', 'São Mateus', 'Conceição da Barra', 'Boa Esperança', 'Pinheiros', 'Pedro Canário', 'Montanha', 'Ponto Belo', 'Mucurici'],
    'Noroeste': ['Águia Branca', 'Mantenópolis', 'Barra de São Francisco', 'Nova Venécia', 'Vila Pavão', 'Água Doce do Norte', 'Ecoporanga'],
}
MUN_PARA_REGIAO = {m: r for r, ms in REGIOES.items() for m in ms}


# ==========================================
# TABELA TOP 10 SALÁRIOS
# ==========================================

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

    # Corte do 0,5% superior (remoção de outliers de salário)
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

    # Nível estadual: agrega a classe primeiro, média ponderada por vínculos, corte de 50.
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


# ==========================================
# PAINEL DE HORAS TRABALHADAS
# ==========================================

def _stats_ponderadas(sub):
    """Estatísticas ponderadas por vínculos sobre as médias de horas por classe."""
    import math
    sub = sub.sort_values('horas')
    h = sub['horas'].tolist()
    w = sub['peso'].tolist()
    total = sum(w)
    if total <= 0 or not h:
        return None

    media = sum(wi * hi for wi, hi in zip(w, h)) / total
    var = sum(wi * (hi - media) ** 2 for wi, hi in zip(w, h)) / total
    std = math.sqrt(var)

    # Mediana ponderada
    acc = 0.0
    mediana = h[-1]
    for hi, wi in zip(h, w):
        acc += wi
        if acc >= total / 2:
            mediana = hi
            break

    return {
        'media': round(media, 1),
        'mediana': round(mediana, 1),
        'desvio': round(std, 1),
        'min': round(min(h), 1),
        'max': round(max(h), 1),
        'ic95_inf': round(max(0.0, media - 1.96 * std), 1),
        'ic95_sup': round(media + 1.96 * std, 1),
        'n_classes': int(len(h)),
        'vinculos': round(total)
    }


def gerar_dados_horas(df):
    """Estatísticas de horas contratadas por município, região e estado."""
    df2 = df.dropna(subset=['media_horas_da_classe', 'media_vinculos_da_classe']).copy()
    df2['cnae_classe_num'] = df2['cnae_classe_num'].apply(lambda x: str(x).split('.')[0].zfill(5))
    df2['peso'] = df2['media_vinculos_da_classe'] * df2['total_cnpjs_no_cep']

    # Uma média de horas por (município, classe); peso = vínculos estimados
    gh = df2.groupby(['id_municipio_nome', 'cnae_classe_num'], as_index=False).agg(
        horas=('media_horas_da_classe', 'first'),
        peso=('peso', 'sum')
    )
    gh = gh[gh['peso'] > 0].copy()

    # Corte de 0,5% em cada cauda (ponderado por vínculos) para remover outliers de horas
    gh = gh.sort_values('horas')
    acum = gh['peso'].cumsum()
    total_peso = gh['peso'].sum()
    inf = acum >= 0.005 * total_peso
    sup = acum <= 0.995 * total_peso
    gh = gh[inf & sup].copy()

    gh['regiao'] = gh['id_municipio_nome'].map(MUN_PARA_REGIAO).fillna('Indefinido')

    stats = {}
    stats['estado'] = _stats_ponderadas(gh)
    for reg, sub in gh.groupby('regiao'):
        stats[f'reg:{reg}'] = _stats_ponderadas(sub)
    for mun, sub in gh.groupby('id_municipio_nome'):
        stats[f'mun:{mun}'] = _stats_ponderadas(sub)

    # Lista de municípios por região (para o filtro em cascata)
    muns_disponiveis = set(gh['id_municipio_nome'].unique())
    regioes_lista = {'Estado': sorted(muns_disponiveis)}
    for reg, ms in REGIOES.items():
        presentes = sorted([m for m in ms if m in muns_disponiveis])
        if presentes:
            regioes_lista[reg] = presentes

    return {'regioes': regioes_lista, 'stats': stats}


def gerar_painel_horas(df):
    """Retorna o JSON do painel de horas para injeção no HTML."""
    return json.dumps(gerar_dados_horas(df), ensure_ascii=False)