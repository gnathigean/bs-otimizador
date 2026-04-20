import json
import os

CONFIG_FILE = "config_elite.json"

def salvar_perfil(config_dict):
    """Salva as configurações atuais no arquivo JSON."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)
        return True, "Configurações salvas no Perfil Elite!"
    except Exception as e:
        return False, f"Erro ao salvar: {e}"

def carregar_perfil():
    """Carrega as configurações salvas. Retorna {} se não existir."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def localizar_bloodstrike():
    """Tenta encontrar o executável do Blood Strike em locais comuns."""
    import platform
    if platform.system() != "Windows": return None
    
    # Locais comuns de instalação
    paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\BloodStrike\Game\BloodStrike.exe"),
        os.path.expandvars(r"%ProgramFiles%\NetEase\BloodStrike\Game\BloodStrike.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\NetEase\BloodStrike\Game\BloodStrike.exe"),
    ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    return None
