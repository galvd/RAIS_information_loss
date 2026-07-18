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
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Nunito:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-page:#FFFFFF;
            --bg-panel:#BBDEFB;
            --bg-panel-soft:#E3F2FD;
            --bg-card:#FFFFFF;
            --blue-dark:#1565C0;
            --blue-mid:#2196F3;
            --blue-border:#90CAF9;
            --blue-muted:#5C84AC;
            --magenta:#F06292;
            --magenta-text:#C2185B;
            --magenta-soft:#FCE4EC;
            --font-display:"Baloo 2", "Nunito", sans-serif;
            --font-body:"Nunito", -apple-system, sans-serif;
        }
        *{ box-sizing:border-box; }
        body { font-family: var(--font-body); background-color: var(--bg-page); color: var(--blue-dark); margin: 0; padding: 20px; line-height:1.5; -webkit-font-smoothing:antialiased; }
        .container { max-width: 1200px; margin: auto; }

        header.top { text-align: center; padding: 16px 0 24px; }
        header.top h1 { font-family: var(--font-display); font-weight:800; font-size: 30px; margin: 0 0 6px; color: var(--blue-dark); }
        header.top p.update { margin: 0; color: var(--blue-mid); font-size: 15px; font-weight:600; }
        .badge-fonte { display:inline-block; margin-top:14px; font-family: var(--font-body); font-weight:700; font-size:12.5px; color: var(--magenta-text); background:#fff; border:1.5px solid var(--magenta); padding:6px 16px; border-radius:20px; }

        .disclaimer { background: var(--bg-panel-soft); color: var(--blue-dark); padding: 12px 16px; border-radius: 10px; font-size: 0.9rem; margin: 20px 0; border-left: 4px solid var(--blue-mid); text-align:left; }
        .intro-text { text-align: justify; margin-bottom: 28px; font-size: 1.02rem; line-height: 1.65; color: var(--blue-muted); }

        .mega-panel { background: var(--bg-panel); border-radius: 24px; padding: 20px; }

        details { background: var(--bg-card); margin-bottom: 14px; border-radius: 16px; overflow: hidden; }
        details:last-child { margin-bottom: 0; }
        summary { padding: 16px 20px; font-family: var(--font-display); font-size: 1.15rem; font-weight: 700; cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center; transition: background 0.25s; color: var(--blue-dark); }
        summary:hover { background: var(--bg-panel-soft); }
        summary::after { content: "▶"; font-size: 0.75rem; color: var(--magenta); transition: transform 0.25s; }
        details[open] summary::after { transform: rotate(90deg); }
        details[open] summary { background: var(--bg-panel-soft); }
        .content { padding: 0; }

        iframe { width: 100%; height: 750px; border: none; display: block; }

        /* Subtítulo interno de bloco */
        .bloco-sub { padding: 16px 20px 4px; font-family: var(--font-display); font-size: 1.05rem; font-weight: 700; color: var(--blue-dark); }

        /* Tabela top 10 */
        .tabela-wrapper { padding: 20px; }
        .tabela-controles { margin-bottom: 15px; display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-end; }
        .tabela-controles label { font-weight: 700; margin-right: 10px; color: var(--blue-dark); font-size: 13px; }
        .tabela-controles select { padding: 8px 12px; font-size: 0.92rem; font-family: var(--font-body); color: var(--blue-dark); background:#fff; border: 1px solid var(--blue-border); border-radius: 8px; min-width: 240px; }
        table.top-salarios { width: 100%; border-collapse: collapse; font-size: 0.94rem; }
        table.top-salarios th, table.top-salarios td { padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--bg-panel-soft); }
        table.top-salarios th { background: var(--blue-dark); color: white; font-weight:700; }
        table.top-salarios td.num { text-align: right; font-variant-numeric: tabular-nums; }
        table.top-salarios tr:nth-child(even) { background: var(--bg-panel-soft); }
        table.top-salarios td.rank { text-align: center; font-weight: 800; color: var(--magenta-text); width: 40px; }
        .nota-metodologica { margin-top: 15px; padding: 12px 16px; font-size: 0.85rem; color: var(--blue-muted); line-height: 1.55; background: var(--bg-panel-soft); border-left: 3px solid var(--blue-mid); border-radius: 8px; }

        /* Painel de horas */
        .horas-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-top: 10px; }
        .horas-card { background: var(--bg-panel-soft); border-radius: 12px; padding: 14px 16px; }
        .horas-card .rotulo { font-size: 0.78rem; color: var(--blue-mid); text-transform: uppercase; letter-spacing: 0.03em; font-weight:700; }
        .horas-card .valor { font-family: var(--font-display); font-size: 1.55rem; font-weight: 700; color: var(--blue-dark); margin-top: 4px; }
        .horas-card .unid { font-size: 0.88rem; font-weight: 500; color: var(--blue-muted); }
        .horas-card.destaque { background: var(--magenta-soft); grid-column: span 2; }
        .horas-card.destaque .valor { color: var(--magenta-text); }
        .horas-meta { margin-top: 12px; font-size: 0.85rem; color: var(--blue-muted); }

        footer { text-align: center; margin-top: 40px; color: var(--blue-muted); font-size: 11.5px; line-height: 1.7; }
        footer .footer-links { margin: 14px 0 0; padding-top: 14px; border-top: 1px solid var(--blue-border); font-size: 12px; }
        footer .footer-links a { color: var(--magenta-text); text-decoration: underline; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <header class="top">
            <h1>Observatório de Empresas do ES</h1>
            <p class="update">Monitor de Emprego e Renda · última atualização: __DATA_ATUALIZACAO__</p>
            <span class="badge-fonte">RAIS + CNPJ · 2025</span>
        </header>

        <div class="disclaimer">
            ⚠️ <strong>Nota:</strong> A renderização inicial dos mapas pode levar alguns segundos devido ao processamento de milhares de hexágonos vetoriais. Recomendado acesso por desktop.
        </div>

        <div class="intro-text">
            <p>Este painel apresenta a distribuição microespacial do mercado de trabalho no ES. Os dados cruzam informações da RAIS e do Cadastro Nacional da Pessoa Jurídica (CNPJ) de 2025, último dado disponível, agregados em grades hexagonais de alta resolução (H3). Essa metodologia protege o sigilo individual das empresas ao mesmo tempo que revela com precisão a densidade econômica, os polos geradores de emprego e as manchas de maior remuneração do território.</p>
        </div>

        <div class="mega-panel">
            <details open>
                <summary>Salários por Atividade Econômica</summary>
                <div class="content">
                    <div class="tabela-wrapper">
                        <div class="tabela-controles">
                            <div>
                                <label for="tab-filtro-reg">Região:</label><br>
                                <select id="tab-filtro-reg" onchange="onRegiaoChangeTabela()"></select>
                            </div>
                            <div>
                                <label for="tab-filtro-mun">Recorte:</label><br>
                                <select id="tab-filtro-mun" onchange="renderTabelaSalarios()"></select>
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
                            <strong>Nota metodológica:</strong> Os salários são apresentados em valor médio nominal refletindo a remuneração média efetivamente contratada por vínculo na classe. Para garantir robustez estatística, foram excluídas as classes CNAE abaixo de um limiar mínimo de vínculos por recorte (<strong>50 no agregado estadual, nos agregados regionais e na Região Metropolitana da Grande Vitória</strong>, e <strong>20 nos demais municípios</strong>), bem como o <strong>0,5% superior</strong> da distribuição salarial (remoção de outliers). Nos agregados estadual e regionais, o salário de cada classe corresponde à média ponderada pelo número de vínculos entre os municípios do recorte.
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
        </div>

        <footer>
            Observatório de Empresas do ES · Monitor de Emprego e Renda
            <p class="footer-links">
                Construído por <strong>Daniel Galvêas</strong> ·
                <a href="https://github.com/galvd" target="_blank" rel="noopener">github.com/galvd</a> ·
                Repositório: <a href="https://github.com/galvd/RAIS_information_loss" target="_blank" rel="noopener">RAIS_information_loss</a> ·
                Dashboard (Looker Studio): <a href="https://lookerstudio.google.com/reporting/c343406e-dbb1-41b7-a2db-56b4801d5101/page/p_eo722dulld" target="_blank" rel="noopener">clique aqui</a><br>
                Projeto irmão: <a href="https://galvd.github.io/irpf/" target="_blank" rel="noopener">Observatório de IRPF do ES</a>
            </p>
        </footer>
    </div>

    <script>
        const DADOS_TABELA = __TABELA_DADOS_JSON__;
        const PAINEL_HORAS = __PAINEL_HORAS_JSON__;

        function renderTabelaSalarios() {
            const chave = document.getElementById('tab-filtro-mun').value;
            const linhas = DADOS_TABELA.stats[chave] || [];
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

        function initTabela() {
            const selReg = document.getElementById('tab-filtro-reg');
            const regioes = Object.keys(DADOS_TABELA.regioes);
            const ordenadas = ['Estado'].concat(regioes.filter(function (r) { return r !== 'Estado'; }).sort());
            selReg.innerHTML = ordenadas.map(function (r) {
                return '<option value="' + r + '">' + (r === 'Estado' ? 'Estado (ES)' : r) + '</option>';
            }).join('');
            onRegiaoChangeTabela();
        }

        function onRegiaoChangeTabela() {
            const reg = document.getElementById('tab-filtro-reg').value;
            const selMun = document.getElementById('tab-filtro-mun');
            const muns = DADOS_TABELA.regioes[reg] || [];
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
            renderTabelaSalarios();
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
            initTabela();
            initHoras();
        });
    </script>
</body>
</html>
"""

# ==========================================
# MOTOR DE INJEÇÃO
# ==========================================

def atualizar_paineis(dados_json, horas_json):
    print("[Web Generator] Gerando página HTML...")
    pasta_raiz = os.getcwd()

    data_formatada = datetime.now().strftime('%d/%m/%Y')

    html_final = (
        TEMPLATE_HTML
        .replace("__DATA_ATUALIZACAO__", data_formatada)
        .replace("__TABELA_DADOS_JSON__", dados_json)
        .replace("__PAINEL_HORAS_JSON__", horas_json)
    )

    caminho_html = os.path.join(pasta_raiz, 'index.html')
    with open(caminho_html, 'w', encoding='utf-8') as f:
        f.write(html_final)
    print(f"  -> HTML criado com sucesso em: {caminho_html}")

    pasta_maps = os.path.join(pasta_raiz, 'maps')
    os.makedirs(pasta_maps, exist_ok=True)