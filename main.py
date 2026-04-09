import os
import pandas as pd
from settings.settings import load_config
from pyfiles.update_html import atualizar_paineis
from pyfiles.map_generator import (
                                    gerar_mapa_estatico_salarios,
                                    gerar_mapa_estatico_vinculos,
                                    gerar_mapa_estatico_cnpjs
)

config = load_config()

PROJ_DIR = config['caminho_rede']
ARQUIVO_DADOS = "salarios_vinculos_ES.csv"

if __name__ == "__main__":
    caminho_dados = os.path.join(PROJ_DIR, 'data', ARQUIVO_DADOS)
    pasta_mapas = os.path.join(PROJ_DIR, 'maps')
    os.makedirs(pasta_mapas, exist_ok=True)

    print("--- ETAPA 1: Leitura da Base Consolidada ---")
    if os.path.exists(caminho_dados):
        df = pd.read_csv(caminho_dados)
        print(f"Dados carregados: {df.shape[0]} registros.")
        
        print("\n--- ETAPA 2: Geração dos Mapas Estáticos ---")
        gerar_mapa_estatico_salarios(df, pasta_destino=pasta_mapas)
        gerar_mapa_estatico_vinculos(df, pasta_destino=pasta_mapas)
        gerar_mapa_estatico_cnpjs(df, pasta_destino=pasta_mapas)

        print("\n--- ETAPA 3: Geração do Dashboard Web (HTML) ---")
        atualizar_paineis()
        
    else:
        print(f"ERRO: Base de dados não encontrada em {caminho_dados}.")