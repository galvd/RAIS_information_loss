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
        .content { padding: 0; } /* Padding zerado para o iframe ocupar todo o espaço */
        
        /* Ajuste de altura para os mapas */
        iframe { width: 100%; height: 750px; border: none; display: block; }
        
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
            <p>Este painel apresenta a distribuição microespacial do mercado de trabalho no ES. Os dados cruzam informações da RAIS e do Cadastro Nacional da Pessoa Jurídica (CNPJ) de 2023, agregados em grades hexagonais de alta resolução (H3). Essa metodologia protege o sigilo individual das empresas ao mesmo tempo que revela com precisão a densidade econômica, os polos geradores de emprego e as manchas de maior remuneração do território.</p>
        </div>

        <details open>
            <summary>Densidade de Salários Normalizados</summary>
            <div class="content"><iframe src="maps/mapa_salarios_estatico.html" loading="lazy"></iframe></div>
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
</body>
</html>
"""

# ==========================================
# MOTOR DE INJEÇÃO
# ==========================================

def atualizar_paineis():
    print("[Web Generator] Gerando página HTML...")
    pasta_raiz = os.getcwd()
    
    data_hoje = datetime.now()
    data_formatada = data_hoje.strftime('%d/%m/%Y')
    
    html_final = TEMPLATE_HTML.replace("__DATA_ATUALIZACAO__", data_formatada)
    
    # Salva o index.html na raiz do projeto (para o GitHub Pages ler)
    caminho_html = os.path.join(pasta_raiz, 'index.html')
    with open(caminho_html, 'w', encoding='utf-8') as f:
        f.write(html_final)
    print(f"  -> HTML criado com sucesso em: {caminho_html}")

    # Salva o README/Markdown base na pasta de mapas
    pasta_maps = os.path.join(pasta_raiz, 'maps')
    os.makedirs(pasta_maps, exist_ok=True)
    

if __name__ == "__main__":
    atualizar_paineis()