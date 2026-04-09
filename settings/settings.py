import sys, json, os

def load_config():
    config_path = os.path.join(os.getcwd(), 'settings', 'config.json')
    with open(config_path) as config_file:
        config = json.load(config_file)
        if config['caminho_rede'] not in sys.path:
            sys.path.append(config['caminho_rede'])
    return config