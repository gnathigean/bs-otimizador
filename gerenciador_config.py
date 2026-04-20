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
    """Tenta encontrar o executável do Blood Strike (Steam ou Launcher)."""
    import platform
    if platform.system() != "Windows": return None
    
    # 1. Tentar detectar via Steam (Caminho mais comum atualmente)
    steam_path = _get_steam_exe_path()
    if steam_path and os.path.exists(steam_path):
        return steam_path

    # 2. Locais comuns de instalação do Launcher Oficial
    paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\BloodStrike\Game\BloodStrike.exe"),
        os.path.expandvars(r"%ProgramFiles%\NetEase\BloodStrike\Game\BloodStrike.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\NetEase\BloodStrike\Game\BloodStrike.exe"),
    ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def detectar_versao_jogo():
    """Retorna qual versão do jogo foi encontrada."""
    path = localizar_bloodstrike()
    if not path:
        return "Não Localizado"
    
    if "steamapps" in path.lower():
        return "Steam Edition"
    else:
        return "Launcher Oficial (NetEase)"

def _get_steam_exe_path():
    """Busca o caminho do executável na instalação da Steam via Registro."""
    import winreg
    try:
        # Tenta pegar o diretório de instalação da Steam no Registro
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steam_base_path, _ = winreg.QueryValueEx(key, "SteamPath")
        winreg.CloseKey(key)
        
        # Caminho padrão na Steam
        steam_exe = os.path.join(steam_base_path, "steamapps", "common", "Blood Strike", "Blood Strike.exe")
        if os.path.exists(steam_exe):
            return steam_exe
            
        # Tenta bibliotecas secundárias (libraryfolders.vdf se fosse avançado, 
        # mas caminhos fixos atendem 90% dos usuários)
        return None
    except:
        return None
