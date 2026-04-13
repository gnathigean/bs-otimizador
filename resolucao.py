import os
import platform
import re

def aplicar_resolucao_esticada():
    """Força o Blood Strike a abrir numa resolução 4:3 esticada (1440x1080) editando o .ini."""
    if platform.system() != "Windows":
        import time; time.sleep(1)
        return True, "✅ (Simulação) Resolução 1440x1080 aplicada!"

    appdata = os.environ.get('LOCALAPPDATA', '')
    pastas_alvo = [os.path.join(appdata, 'NetEase', 'BloodStrike', 'Saved', 'Config', 'WindowsNoEditor')]
    
    try:
        for pasta in pastas_alvo:
            if os.path.exists(pasta):
                for root, dirs, files in os.walk(pasta):
                    for file in files:
                        if file == 'GameUserSettings.ini':
                            caminho_arquivo = os.path.join(root, file)
                            
                            with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                                conteudo = f.read()
                            
                            # Força 1440x1080
                            novo = re.sub(r'ResolutionSizeX=[0-9]+', 'ResolutionSizeX=1440', conteudo)
                            novo = re.sub(r'ResolutionSizeY=[0-9]+', 'ResolutionSizeY=1080', novo)
                            novo = re.sub(r'LastUserConfirmedResolutionSizeX=[0-9]+', 'LastUserConfirmedResolutionSizeX=1440', novo)
                            novo = re.sub(r'LastUserConfirmedResolutionSizeY=[0-9]+', 'LastUserConfirmedResolutionSizeY=1080', novo)
                            
                            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                                f.write(novo)
                            
        return True, "✅ Resolução Esticada (1440x1080) aplicada no jogo!"
    except Exception as e:
        return False, f"⚠️ Erro ao esticar resolução: {e}"

def reverter_resolucao():
    return True, "Forçar Resolução Esticada (Vantagem de Hitbox)"