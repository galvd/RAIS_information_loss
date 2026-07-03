# Mapa de Emprego e Renda: Distribuição Espacial (RAIS/CNPJ)

Este repositório contém a infraestrutura em Python para processamento e visualização espacial de dados de emprego, renda e densidade empresarial. O projeto cruza dados da RAIS e do Cadastro Nacional da Pessoa Jurídica (CNPJ) para gerar mapas de calor em grades hexagonais de alta resolução (H3 da Uber), um ranking setorial de salários e um painel de estatísticas de horas trabalhadas. Essa metodologia protege, mesmo utilizando dados públicos abertos, o sigilo individual das empresas ao mesmo tempo que revela com precisão a densidade econômica e o mercado de trabalho no Espírito Santo (ES).

**[Clique aqui para acessar painel com os mapas](https://galvd.github.io/RAIS_information_loss/)**

## Possibilidades Analíticas

A base de dados consolidada possui as seguintes colunas estruturais: `data`, `total_cnpjs_no_cep`, `cep`, `id_municipio_nome`, `cnae_subclasse`, `cnae_subclasse_desc`, `cnae_classe_num`, `cnae_classe_desc`, `media_salarial_da_classe`, `media_horas_da_classe`, `media_vinculos_da_classe`, `centroide_cep`.

Com base nessa estrutura, as principais frentes de análise são:

1. **Micro-Geolocalização Econômica:**
   * Utilização do `centroide_cep` para mapear a economia em nível de rua/bairro, superando as limitações de médias agregadas por município.
   * Identificação de polos de alta densidade empregatícia através do cruzamento de `total_cnpjs_no_cep` e `media_vinculos_da_classe`.

2. **Análise Setorial (CNAE):**
   * Filtragem em diferentes níveis de granularidade: Classe (`cnae_classe_num`) ou Subclasse (`cnae_subclasse`).
   * Ranking dos setores de maior remuneração por município (tabela Top 10, ver abaixo).
   * Comparação de rentabilidade espacial entre setores.

3. **Cálculo de Massa Salarial Real:**
   * A combinação da `media_salarial_da_classe` com a densidade estimada de vínculos permite calcular o volume de dinheiro circulante em um raio específico, essencial para análises de geomarketing e políticas públicas.

4. **Jornada de Trabalho:**
   * A `media_horas_da_classe` (média de horas contratadas semanais por vínculo) permite comparar a intensidade de jornada entre setores e territórios, distinguindo remuneração de carga horária.

## Organização do Dashboard

O `index.html` é gerado dinamicamente em tempo de build (via `table_generator.py` e `update_html.py`); não há dados fixos no HTML. O painel é organizado em blocos temáticos:

* **Salários por Atividade Econômica:** tabela dinâmica (Top 10 classes CNAE por salário médio, com filtro por município) acompanhada do mapa de densidade salarial.
* **Horas Trabalhadas:** painel de estatísticas (média, mediana, desvio-padrão, mínimo, máximo e intervalo de 95%) com filtros em cascata por região e município, acompanhado do mapa de horas contratadas.
* **Concentração de Vínculos** e **Densidade Empresarial (CNPJs):** mapas independentes.

### Notas metodológicas — salários

* Valor médio nominal, refletindo a remuneração média efetivamente contratada por vínculo na classe.
* Exclusão de classes CNAE com menos de 50 vínculos na Região Metropolitana e menos de 20 vínculos nos demais municípios.
* Corte do 0,5% superior da distribuição salarial (remoção de outliers).
* No agregado estadual, salário por classe é a média ponderada pelo número de vínculos entre municípios (também com corte de 50 vínculos).

### Notas metodológicas — horas trabalhadas

* Horas contratadas semanais por vínculo (RAIS), agregadas por município, região (microrregiões de planejamento do ES) e estado.
* Estatísticas ponderadas pelo número de vínculos, calculadas sobre as médias por classe CNAE — medem dispersão entre setores, não entre trabalhadores individuais.
* Corte de 0,5% em cada cauda da distribuição de horas (remoção de outliers).
* Intervalo de 95% = média ± 1,96 desvio-padrão (aproximação da faixa de jornada da maioria dos vínculos).

## Estrutura do Projeto

O código segue uma arquitetura modular para facilitar a manutenção e escalabilidade.

```text
/
├── main.py                     # Orquestrador central de execução
├── index.html                  # Dashboard web gerado dinamicamente para o GitHub Pages
├── settings/
│   ├── __init__.py
│   ├── config.json             # Configuração de caminhos do sistema (Ignorado no Git)
│   └── settings.py             # Loader de configurações
├── pyfiles/
│   ├── __init__.py
│   ├── map_utils.py            # Funções auxiliares (H3, formatação, injeção de JS/CSS)
│   ├── map_generator.py        # Lógica de renderização das camadas geográficas no Folium
│   ├── table_generator.py      # Ranking Top 10 de salários e painel de estatísticas de horas
│   └── update_html.py          # Motor de geração e atualização do template HTML base
├── data/                       # Diretório da base de dados local (.csv)
└── maps/                       # Diretório de saída dos iframes dos mapas (.html)
```

## Mapas Gerados

A execução do pipeline lê a base de dados e gera mapas em HTML na pasta `/maps`, além de atualizar a página inicial `index.html`:

1. **`mapa_salarios_estatico.html`**: densidade de salários (média ponderada por vínculos).
2. **`mapa_horas_estatico.html`**: média de horas contratadas semanais por vínculo, ponderada por classe CNAE.
3. **`mapa_vinculos_estatico.html`**: concentração absoluta de vínculos (empregos formais).
4. **`mapa_cnpjs_estatico.html`**: densidade empresarial, concentração de CNPJs ativos (excluindo MEIs).

## Requisitos e Configurações

1. **Requisitos:**
   * Python 3.9+
   * Pacotes: `pandas`, `shapely`, `h3`, `folium`, `branca`

2. **Configuração:**
   Crie o arquivo `settings/config.json` com o caminho raiz do repositório no seu ambiente local:
   ```json
   {
       "caminho_rede": "C:\\Caminho\\Absoluto\\Para\\O\\Projeto"
   }
   ```