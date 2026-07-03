# Mapa de Emprego e Renda: Distribuição Espacial (RAIS/CNPJ)

Este repositório contém a infraestrutura em Python para processamento e visualização espacial de dados de emprego, renda e densidade empresarial. O projeto cruza dados da RAIS e do Cadastro Nacional da Pessoa Jurídica (CNPJ) para gerar mapas de calor em grades hexagonais de alta resolução (H3 da Uber) e um ranking setorial de salários. Essa metodologia protege, mesmo utilizando dados públicos abertos, o sigilo individual das empresas ao mesmo tempo que revela com precisão a densidade econômica e o mercado de trabalho no Espírito Santo (ES).

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

## Ranking Salarial (Tabela Top 10)

O dashboard exibe uma tabela dinâmica com as 10 classes CNAE de maior salário médio, com filtro por município. A tabela é gerada em tempo de build (via `table_generator.py`) e injetada no `index.html`; não há dados fixos no HTML.

**Notas metodológicas do salário:**

* Os salários são apresentados em **valor médio nominal**, refletindo a remuneração média efetivamente contratada por vínculo na classe.
* São excluídas as classes CNAE com **menos de 50 vínculos** no recorte da região metropolitana e **menos de 20 vínculos** para os demais municípios, garantindo robustez estatística.
* É aplicado um corte do **0,5% superior** da distribuição salarial para remoção de outliers.
* No agregado estadual ("Todos os Municípios"), o salário de cada classe é a **média ponderada pelo número de vínculos** entre os municípios, também retirando classes CNAE com menos de 50 vínculos.

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
│   ├── table_generator.py      # Agregação e ranking Top 10 de salários por classe CNAE
│   └── update_html.py          # Motor de geração e atualização do template HTML base
├── data/                       # Diretório da base de dados local (.csv)
└── maps/                       # Diretório de saída dos iframes dos mapas (.html)
```

## Mapas Gerados

A execução do pipeline lê a base de dados e gera mapas em HTML na pasta `/maps`, além de atualizar a página inicial `index.html`:

1. **`mapa_salarios_estatico.html`**: Mapa de calor indicando a densidade de salários (média ponderada por vínculos).
2. **`mapa_horas_estatico.html`**: Média de horas contratadas semanais por vínculo, ponderada por classe CNAE.
3. **`mapa_vinculos_estatico.html`**: Distribuição espacial demonstrando a concentração absoluta de vínculos (empregos formais).
4. **`mapa_cnpjs_estatico.html`**: Visualização da densidade empresarial, evidenciando a concentração de CNPJs ativos (excluindo MEIs).

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