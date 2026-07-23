import json
import math
import unicodedata


def chave_alfabetica(texto):
    """Chave de ordenacao que ignora acentos/cedilha, para que 'Águia Branca'
    e 'São Mateus' fiquem na posicao alfabetica correta (ao lado de 'A...' e
    'S...' sem acento), em vez de irem parar no fim por causa do codigo
    Unicode das letras acentuadas. O texto original (com acento) continua
    sendo exibido normalmente; a chave e usada so para comparacao."""
    sem_acento = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return sem_acento.lower()


# ==========================================
# METODOLOGIA
# ==========================================
# Espelha o tratamento do aggregator.py do Observatorio de Empresas do ES.
# Sao dois arquivos independentes por opcao de projeto: se alterar aqui,
# altere la tambem, senao os dois paineis voltam a divergir.

# Municípios da Região Metropolitana da Grande Vitória (limiar de 50 vínculos)
RMGV = {'Vitória', 'Vila Velha', 'Serra', 'Cariacica', 'Viana', 'Guarapari', 'Fundão'}
LIMIAR_RMGV = 50        # agregado estadual, agregados regionais e municípios da RMGV
LIMIAR_INTERIOR = 20    # demais municípios
OUTLIER_SUP = 0.995     # mantém os 99,5% inferiores da distribuição
OUTLIER_INF = 0.005     # cauda inferior (usada só nas horas)

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


def cnae_key(x):
    """Chave canonica da classe CNAE: 5 digitos, string.

    O codigo trafega entre BigQuery, CSV e JSON e pode chegar como float
    ('1113.0'), int (1113) ou sem o zero a esquerda ('1113'). Sem normalizar,
    a chave nao casa entre os paineis e o cruzamento falha em silencio."""
    return str(x).split('.')[0].strip().zfill(5)


def limiar_do_municipio(municipio):
    return LIMIAR_RMGV if municipio in RMGV else LIMIAR_INTERIOR


def corte_ponderado(df, col_valor, col_peso, sup=OUTLIER_SUP, inf=None):
    """Corte de cauda PONDERADO POR VINCULOS.

    Ponderado = corta os 0,5% dos TRABALHADORES no extremo, nao as 0,5% das
    LINHAS de maior valor. A diferenca e decisiva: as linhas (municipio, classe)
    com 1 a 15 vinculos tem medias erraticas, ocupam o topo da distribuicao e
    definem o cutoff, derrubando junto classes legitimas logo abaixo.

    Medido no dado real de 2025: o corte por linha -- g['salario'].quantile(0.995),
    que era o metodo usado aqui -- removia 57 linhas somando apenas 1,2% dos
    trabalhadores; eliminava "Bancos de Desenvolvimento" (172 vinculos) por ficar
    2,2% acima do cutoff, e descartava Vitoria inteira da classe 06000 -- 2.117
    dos 2.711 trabalhadores -- publicando "Extracao de petroleo = R$ 10.410"
    calculado sobre 451 pessoas.

    `inf` corta tambem a cauda inferior (usado nas horas, que tem outlier
    relevante nas duas pontas: jornadas minimas e jornadas irreais).
    """
    d = df.dropna(subset=[col_valor]).copy()
    d = d[d[col_peso] > 0]
    if d.empty:
        return d
    d = d.sort_values(col_valor)
    total = float(d[col_peso].sum())
    if total <= 0:
        return d
    acum = d[col_peso].cumsum()
    mask = acum <= sup * total
    if inf is not None:
        mask &= acum >= inf * total
    return d[mask].copy()


def limiar_municipal(g, col_peso='vinculos'):
    """Exclui (municipio, classe) abaixo do limiar do municipio: RMGV 50, demais 20."""
    v = g.groupby(['id_municipio_nome', 'cnae_classe_num'])[col_peso].transform('sum')
    lim = g['id_municipio_nome'].map(limiar_do_municipio)
    return g[v >= lim].copy()


def limiar_agregado(g, chaves_extra=None, col_peso='vinculos', limiar=LIMIAR_RMGV):
    """Exclui classes abaixo do limiar no agregado. chaves_extra=['regiao'] aplica
    o limiar DENTRO de cada regiao; None aplica no total estadual."""
    chaves = list(chaves_extra or []) + ['cnae_classe_num']
    v = g.groupby(chaves)[col_peso].transform('sum')
    return g[v >= limiar].copy()


def media_ponderada(g, chaves, col_valor='salario', col_peso='vinculos'):
    """Agrega por `chaves` com media ponderada por vinculos."""
    d = g.copy()
    d['_ws'] = d[col_valor] * d[col_peso]
    out = d.groupby(chaves, as_index=False).agg(_ws=('_ws', 'sum'),
                                                vinculos=(col_peso, 'sum'))
    out[col_valor] = out['_ws'] / out['vinculos']
    return out.drop(columns='_ws')


# ==========================================
# TABELA TOP 10 SALÁRIOS
# ==========================================

def _top10_linhas(sub):
    """Converte um recorte (ja filtrado pelo limiar) nas 10 linhas de maior salario."""
    top = sub.sort_values('salario', ascending=False).head(10)
    return [
        {
            'classe': r['cnae_classe_num'],
            'desc': r['cnae_classe_desc'],
            'salario': round(float(r['salario']), 2),
            'vinculos': float(r['vinculos'])
        }
        for _, r in top.iterrows()
    ]


def gerar_dados_tabela(df):
    """Agrega por município + classe CNAE. Retorna {'stats': {...}, 'regioes': {...}},
    no mesmo padrão do painel de horas trabalhadas: chaves 'mun:MUNICIPIO',
    'reg:REGIAO' e 'estado' em stats, e a lista de municípios por região em
    'regioes' para alimentar o filtro em cascata Região -> Recorte.

    Metodologia (identica ao aggregator.py do Observatorio):
      1. corte do 0,5% superior PONDERADO POR VINCULOS, aplicado UMA VEZ sobre
         as linhas (municipio, classe);
      2. limiar minimo de vinculos por recorte, aplicado DEPOIS do corte;
      3. media ponderada por vinculos dentro de cada recorte.

    Cada recorte usa sua propria base filtrada, porque o limiar e POR RECORTE:
    uma classe pequena pode nao passar num municipio do interior e passar no
    agregado estadual. Filtrar uma vez so daria numeros inconsistentes entre
    os cortes.
    """
    df2 = df.dropna(subset=['media_salarial_da_classe', 'media_vinculos_da_classe']).copy()

    df2['cnae_classe_num'] = df2['cnae_classe_num'].apply(cnae_key)
    df2['cnae_classe_desc'] = df2['cnae_classe_desc'].fillna('Indefinido').astype(str)
    df2['vinc_row'] = df2['media_vinculos_da_classe'] * df2['total_cnpjs_no_cep']

    g = df2.groupby(
        ['id_municipio_nome', 'cnae_classe_num', 'cnae_classe_desc'], as_index=False
    ).agg(
        salario=('media_salarial_da_classe', 'first'),
        vinculos=('vinc_row', 'sum')
    )

    # 1. Corte do 0,5% superior, ponderado por vinculos.
    g = corte_ponderado(g, col_valor='salario', col_peso='vinculos', sup=OUTLIER_SUP)
    if g.empty:
        return {'stats': {}, 'regioes': {}}
    g['regiao'] = g['id_municipio_nome'].map(MUN_PARA_REGIAO).fillna('Indefinido')

    stats = {}
    chaves_classe = ['cnae_classe_num', 'cnae_classe_desc']

    # 2a. Por municipio: limiar por porte (RMGV 50, interior 20).
    base_mun = limiar_municipal(g)
    for mun, sub in base_mun.groupby('id_municipio_nome'):
        linhas = _top10_linhas(media_ponderada(sub, chaves_classe))
        if linhas:
            stats[f'mun:{mun}'] = linhas

    # 2b. Por regiao de planejamento: limiar 50 sobre o total DA REGIAO,
    #     media ponderada entre os municipios da regiao.
    base_reg = limiar_agregado(g, chaves_extra=['regiao'])
    for reg, sub in base_reg.groupby('regiao'):
        linhas = _top10_linhas(media_ponderada(sub, chaves_classe))
        if linhas:
            stats[f'reg:{reg}'] = linhas

    # 2c. Estado: limiar 50 sobre o total estadual.
    base_est = limiar_agregado(g)
    if not base_est.empty:
        stats['estado'] = _top10_linhas(media_ponderada(base_est, chaves_classe))

    # Lista de municípios por região, para o filtro em cascata (mesmo padrão do painel de horas)
    muns_disponiveis = set(g['id_municipio_nome'].unique())
    regioes_lista = {'Estado': sorted(muns_disponiveis, key=chave_alfabetica)}
    for reg, ms in REGIOES.items():
        presentes = sorted([m for m in ms if m in muns_disponiveis], key=chave_alfabetica)
        if presentes:
            regioes_lista[reg] = presentes

    return {'stats': stats, 'regioes': regioes_lista}


def gerar_tabela_salarios(df):
    """Retorna o JSON pronto para injeção no HTML (estrutura com 'stats' e
    'regioes', no mesmo padrão do painel de horas). ATENÇÃO: esta função deixou
    de devolver (dados_json, mun_options) — agora devolve só dados_json, já que
    o dropdown de município é montado dinamicamente em JS a partir de 'regioes',
    e não mais gerado como HTML pronto no Python."""
    dados = gerar_dados_tabela(df)
    return json.dumps(dados, ensure_ascii=False)


# ==========================================
# PAINEL DE HORAS TRABALHADAS
# ==========================================

def _stats_ponderadas(sub):
    """Estatísticas ponderadas por vínculos sobre as médias de horas por classe."""
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
    """Estatísticas de horas contratadas por município, região e estado.

    Mesma metodologia do painel de salarios: corte ponderado (aqui nas DUAS
    caudas, porque horas tem outlier relevante nas duas pontas) e limiar minimo
    de vinculos por recorte."""
    df2 = df.dropna(subset=['media_horas_da_classe', 'media_vinculos_da_classe']).copy()
    df2['cnae_classe_num'] = df2['cnae_classe_num'].apply(cnae_key)
    df2['peso'] = df2['media_vinculos_da_classe'] * df2['total_cnpjs_no_cep']

    # Uma média de horas por (município, classe); peso = vínculos estimados
    gh = df2.groupby(['id_municipio_nome', 'cnae_classe_num'], as_index=False).agg(
        horas=('media_horas_da_classe', 'first'),
        peso=('peso', 'sum')
    )
    gh = gh[gh['peso'] > 0].copy()

    # 1. Corte de 0,5% em cada cauda, ponderado por vínculos.
    gh = corte_ponderado(gh, col_valor='horas', col_peso='peso',
                         sup=OUTLIER_SUP, inf=OUTLIER_INF)
    if gh.empty:
        return {'regioes': {}, 'stats': {}}
    gh['regiao'] = gh['id_municipio_nome'].map(MUN_PARA_REGIAO).fillna('Indefinido')

    # 2. Limiar de vinculos por recorte (mesma regra dos salarios).
    stats = {}
    base_est = limiar_agregado(gh, col_peso='peso')
    if not base_est.empty:
        stats['estado'] = _stats_ponderadas(base_est)

    base_reg = limiar_agregado(gh, chaves_extra=['regiao'], col_peso='peso')
    for reg, sub in base_reg.groupby('regiao'):
        st = _stats_ponderadas(sub)
        if st:
            stats[f'reg:{reg}'] = st

    base_mun = limiar_municipal(gh, col_peso='peso')
    for mun, sub in base_mun.groupby('id_municipio_nome'):
        st = _stats_ponderadas(sub)
        if st:
            stats[f'mun:{mun}'] = st

    # Lista de municípios por região (para o filtro em cascata)
    muns_disponiveis = set(gh['id_municipio_nome'].unique())
    regioes_lista = {'Estado': sorted(muns_disponiveis, key=chave_alfabetica)}
    for reg, ms in REGIOES.items():
        presentes = sorted([m for m in ms if m in muns_disponiveis], key=chave_alfabetica)
        if presentes:
            regioes_lista[reg] = presentes

    return {'regioes': regioes_lista, 'stats': stats}


def gerar_painel_horas(df):
    """Retorna o JSON do painel de horas para injeção no HTML."""
    return json.dumps(gerar_dados_horas(df), ensure_ascii=False)