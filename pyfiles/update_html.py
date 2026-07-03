import os
from datetime import datetime

# ==========================================
# TEMPLATES
# ==========================================

TEMPLATE_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Observatório de Empresas do ES: Monitor de Emprego e Renda</title>
    <style>
        :root { --primary: #2c3e50; --accent: #e34a33; --bg: #f8f9fa; --text: #333; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background-color: var(--bg); color: var(--text); margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: auto; }
        .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #eee; padding-bottom: 20px; }
        .disclaimer { background: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; font-size: 0.9rem; margin-bottom: 20px; border: 1px solid #ffeeba; }
        .intro-text { text-align: justify; margin-bottom: 30px; font-size: 1.05rem; line-height: 1.6; color: #444; }

        details { background: white; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; border: 1px solid #ddd; }
        summary { padding: 15px 20px; font-size: 1.2rem; font-weight: bold; cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center; transition: background 0.3s; color: var(--primary); }
        summary:hover { background: #f1f1f1; }
        summary::after { content: "▶"; font-size: 0.8rem; transition: transform 0.3s; }
        details[open] summary::after { transform: rotate(90deg); }
        details[open] summary { border-bottom: 1px solid #eee; background: #fafafa; }
        .content { padding: 0; }

        iframe { width: 100%; height: 750px; border: none; display: block; }

        /* Subtítulo interno de bloco */
        .bloco-sub { padding: 16px 20px 4px; font-size: 1.05rem; font-weight: bold; color: var(--primary); border-top: 1px solid #eee; }

        /* Tabela top 10 */
        .tabela-wrapper { padding: 20px; }
        .tabela-controles { margin-bottom: 15px; display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-end; }
        .tabela-controles label { font-weight: bold; margin-right: 10px; }
        .tabela-controles select { padding: 6px 10px; font-size: 0.95rem; border: 1px solid #ccc; border-radius: 5px; min-width: 240px; }
        table.top-salarios { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
        table.top-salarios th, table.top-salarios td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; }
        table.top-salarios th { background: var(--primary); color: white; }
        table.top-salarios td.num { text-align: right; font-variant-numeric: tabular-nums; }
        table.top-salarios tr:nth-child(even) { background: #f6f8fa; }
        table.top-salarios td.rank { text-align: center; font-weight: bold; color: var(--accent); width: 40px; }
        .nota-metodologica { margin-top: 15px; padding: 12px 15px; font-size: 0.85rem; color: #555; line-height: 1.5; background: #f1f3f5; border-left: 3px solid var(--primary); border-radius: 4px; }

        /* Painel de horas */
        .horas-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-top: 10px; }
        .horas-card { background: #f6f8fa; border: 1px solid #e3e7eb; border-radius: 8px; padding: 14px 16px; }
        .horas-card .rotulo { font-size: 0.8rem; color: #777; text-transform: uppercase; letter-spacing: 0.03em; }
        .horas-card .valor { font-size: 1.6rem; font-weight: bold; color: var(--primary); margin-top: 4px; }
        .horas-card .unid { font-size: 0.9rem; font-weight: normal; color: #999; }
        .horas-card.destaque { background: #fdeee9; border-color: #f2c4b6; grid-column: span 2; }
        .horas-card.destaque .valor { color: var(--accent); }
        .horas-meta { margin-top: 12px; font-size: 0.85rem; color: #666; }

        .links-topo { margin: 15px 0; line-height: 1.6; }
        .links-topo a { color: var(--accent); text-decoration: none; font-weight: bold; }
        .links-topo a:hover { text-decoration: underline; }
        .footer { text-align: center; margin-top: 50px; padding: 20px; font-size: 0.9rem; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Observatório de Empresas do ES: Monitor de Emprego e Renda</h1>
            <p>Última atualização: __DATA_ATUALIZACAO__</p>
            <div class="links-topo">
                <p>Construído por <strong>Daniel Galvêas</strong> - <a href="https://github.com/galvd" target="_blank">github.com/galvd</a></p>
                <p>Para visualizar o repositório deste projeto no Github, <a href="https://github.com/galvd/RAIS_information_loss" target="_blank">clique aqui</a>.</p>
                <p>Para visualizar o dashboard do Observatório de Empresas do ES, <a href="https://lookerstudio.google.com/reporting/c343406e-dbb1-41b7-a2db-56b4801d5101/page/p_eo722dulld" target="_blank">clique aqui</a>.</p>
            </div>
            <div class="disclaimer">
                ⚠️ <strong>Nota:</strong> A renderização inicial dos mapas pode levar alguns segundos devido ao processamento de milhares de hexágonos vetoriais. Recomendado acesso por desktop.
            </div>
        </header>

        <div class="intro-text">
            <p>Este painel apresenta a distribuição microespacial do mercado de trabalho no ES. Os dados cruzam informações da RAIS e do Cadastro Nacional da Pessoa Jurídica (CNPJ) de 2025, último dado disponível, agregados em grades hexagonais de alta resolução (H3). Essa metodologia protege o sigilo individual das empresas ao mesmo tempo que revela com precisão a densidade econômica, os polos geradores de emprego e as manchas de maior remuneração do território.</p>
        </div>

        <details open>
            <summary>Salários por Atividade Econômica</summary>
            <div class="content">
                <div class="tabela-wrapper">
                    <div class="tabela-controles">
                        <div>
                            <label for="tab-filtro-mun">Município:</label><br>
                            <select id="tab-filtro-mun" onchange="renderTabelaSalarios()">
                                __TABELA_MUN_OPTIONS__
                            </select>
                        </div>
                    </div>
                    <table class="top-salarios">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Classe CNAE</th>
                                <th style="text-align:right;">Salário Médio (R$)</th>
                                <th style="text-align:right;">Total de Vínculos</th>
                            </tr>
                        </thead>
                        <tbody id="tab-body"></tbody>
                    </table>
                    <div class="nota-metodologica">
                        <strong>Nota metodológica:</strong> Os salários são apresentados em valor médio nominal refletindo a remuneração média efetivamente contratada por vínculo na classe. Para garantir robustez estatística, foram excluídas as classes CNAE abaixo de um limiar mínimo de vínculos por recorte (<strong>50 na Região Metropolitana da Grande Vitória</strong> e <strong>20 nos demais municípios</strong>), bem como o <strong>0,5% superior</strong> da distribuição salarial (remoção de outliers). No agregado estadual ("Todos os Municípios"), o salário de cada classe corresponde à média ponderada pelo número de vínculos entre os municípios.
                    </div>
                </div>
                <div class="bloco-sub">Distribuição espacial dos salários</div>
                <iframe src="maps/mapa_salarios_estatico.html" loading="lazy"></iframe>
            </div>
        </details>

        <details>
            <summary>Horas Trabalhadas</summary>
            <div class="content">
                <div class="tabela-wrapper">
                    <div class="tabela-controles">
                        <div>
                            <label for="horas-filtro-reg">Região:</label><br>
                            <select id="horas-filtro-reg" onchange="onRegiaoChange()"></select>
                        </div>
                        <div>
                            <label for="horas-filtro-mun">Recorte:</label><br>
                            <select id="horas-filtro-mun" onchange="renderHoras()"></select>
                        </div>
                    </div>
                    <div class="horas-grid" id="horas-grid"></div>
                    <div class="horas-meta" id="horas-meta"></div>
                    <div class="nota-metodologica">
                        <strong>Nota metodológica:</strong> Refere-se às <strong>horas contratadas semanais</strong> por vínculo (RAIS). Como a base disponibiliza a média por classe CNAE, média, mediana, desvio-padrão e o intervalo de 95% são calculados sobre a distribuição das médias por classe, ponderadas pelo número de vínculos. Foi aplicado corte de 0,5% em cada cauda da distribuição de horas (remoção de outliers). O intervalo de 95% (média ± 1,96 desvio-padrão) é uma aproximação da faixa em que se concentra a jornada da maioria dos vínculos formais.
                    </div>
                </div>
                <div class="bloco-sub">Distribuição espacial das horas contratadas</div>
                <iframe src="maps/mapa_horas_estatico.html" loading="lazy"></iframe>
            </div>
        </details>

        <details>
            <summary>Concentração de Vínculos (Empregos)</summary>
            <div class="content"><iframe src="maps/mapa_vinculos_estatico.html" loading="lazy"></iframe></div>
        </details>

        <details>
            <summary>Densidade Empresarial (CNPJs sem MEIs)</summary>
            <div class="content"><iframe src="maps/mapa_cnpjs_estatico.html" loading="lazy"></iframe></div>
        </details>

        <footer class="footer">Observatório das Empresas do ES</footer>
    </div>

    <script>
        const DADOS_TABELA = __TABELA_DADOS_JSON__;
        const PAINEL_HORAS = __PAINEL_HORAS_JSON__;

        function renderTabelaSalarios() {
            const mun = document.getElementById('tab-filtro-mun').value;
            const linhas = DADOS_TABELA[mun] || [];
            const tbody = document.getElementById('tab-body');
            tbody.innerHTML = linhas.map(function (r, i) {
                const sal = r.salario.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                const vin = Math.round(r.vinculos).toLocaleString('pt-BR');
                return '<tr>' +
                    '<td class="rank">' + (i + 1) + '</td>' +
                    '<td>' + r.classe + ' - ' + r.desc + '</td>' +
                    '<td class="num">' + sal + '</td>' +
                    '<td class="num">' + vin + '</td>' +
                    '</tr>';
            }).join('');
        }

        // ---- Painel de horas ----
        function initHoras() {
            const selReg = document.getElementById('horas-filtro-reg');
            const regioes = Object.keys(PAINEL_HORAS.regioes);
            const ordenadas = ['Estado'].concat(regioes.filter(function (r) { return r !== 'Estado'; }).sort());
            selReg.innerHTML = ordenadas.map(function (r) {
                return '<option value="' + r + '">' + (r === 'Estado' ? 'Estado (ES)' : r) + '</option>';
            }).join('');
            onRegiaoChange();
        }

        function onRegiaoChange() {
            const reg = document.getElementById('horas-filtro-reg').value;
            const selMun = document.getElementById('horas-filtro-mun');
            const muns = PAINEL_HORAS.regioes[reg] || [];
            let opts;
            if (reg === 'Estado') {
                opts = ['<option value="estado">Agregado do Estado</option>'];
            } else {
                opts = ['<option value="reg:' + reg + '">Agregado da Região</option>'];
            }
            opts = opts.concat(muns.map(function (m) {
                return '<option value="mun:' + m + '">' + m + '</option>';
            }));
            selMun.innerHTML = opts.join('');
            renderHoras();
        }

        function card(rotulo, valor, unid, destaque) {
            return '<div class="horas-card' + (destaque ? ' destaque' : '') + '">' +
                '<div class="rotulo">' + rotulo + '</div>' +
                '<div class="valor">' + valor + (unid ? ' <span class="unid">' + unid + '</span>' : '') + '</div>' +
                '</div>';
        }

        function renderHoras() {
            const chave = document.getElementById('horas-filtro-mun').value;
            const s = PAINEL_HORAS.stats[chave];
            const grid = document.getElementById('horas-grid');
            const meta = document.getElementById('horas-meta');
            if (!s) {
                grid.innerHTML = '';
                meta.textContent = 'Sem dados suficientes para este recorte.';
                return;
            }
            grid.innerHTML =
                card('Média', s.media, 'h/sem') +
                card('Mediana', s.mediana, 'h/sem') +
                card('Desvio-padrão', s.desvio, 'h') +
                card('Mínimo', s.min, 'h/sem') +
                card('Máximo', s.max, 'h/sem') +
                card('Intervalo de 95% dos vínculos', s.ic95_inf + ' – ' + s.ic95_sup, 'h/sem', true);
            meta.textContent = 'Base: ' + s.n_classes.toLocaleString('pt-BR') +
                ' classes CNAE · ' + s.vinculos.toLocaleString('pt-BR') + ' vínculos estimados.';
        }

        document.addEventListener('DOMContentLoaded', function () {
            renderTabelaSalarios();
            initHoras();
        });
    </script>
</body>
</html>
"""

# ==========================================
# MOTOR DE INJEÇÃO
# ==========================================

def atualizar_paineis(dados_json, mun_options, horas_json):
    print("[Web Generator] Gerando página HTML...")
    pasta_raiz = os.getcwd()

    data_formatada = datetime.now().strftime('%d/%m/%Y')

    html_final = (
        TEMPLATE_HTML
        .replace("__DATA_ATUALIZACAO__", data_formatada)
        .replace("__TABELA_MUN_OPTIONS__", mun_options)
        .replace("__TABELA_DADOS_JSON__", dados_json)
        .replace("__PAINEL_HORAS_JSON__", horas_json)
    )

    caminho_html = os.path.join(pasta_raiz, 'index.html')
    with open(caminho_html, 'w', encoding='utf-8') as f:
        f.write(html_final)
    print(f"  -> HTML criado com sucesso em: {caminho_html}")

    pasta_maps = os.path.join(pasta_raiz, 'maps')
    os.makedirs(pasta_maps, exist_ok=True)