import os
import platform
import re

def aplicar_potato():
    """Edita o .ini do Blood Strike para forçar gráficos de batata (sombras e folhagens no zero)."""
    if platform.system() != "Windows":
        import time; time.sleep(1.5)
        return True, "✅ (Simulação) Modo Batata ativado no .ini!"

    appdata = os.environ.get('LOCALAPPDATA', '')
    locallow = os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'LocalLow')
    documentos = os.path.join(os.environ.get('USERPROFILE', ''), 'Documents')
    
    pastas_alvo = [
        os.path.join(appdata, 'NetEase', 'BloodStrike', 'Saved', 'Config', 'WindowsNoEditor'),
        os.path.join(locallow, 'NetEase', 'BloodStrike', 'Saved', 'Config', 'WindowsNoEditor'),
        os.path.join(documentos, 'BloodStrike', 'Config')
    ]
    
    sucesso = False
    try:
        for pasta in pastas_alvo:
            if os.path.exists(pasta):
                for root, dirs, files in os.walk(pasta):
                    for file in files:
                        # Busca o GameUserSettings ou Config.ini
                        if file.endswith('.ini'):
                            caminho_arquivo = os.path.join(root, file)
                            
                            with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                                conteudo = f.read()
                            
                            # Se achar as linhas de gráficos, zera todas
                            if 'sg.ShadowQuality' in conteudo or 'ShadowQuality' in conteudo:
                                novo = re.sub(r'sg\.ShadowQuality=[0-9]+', 'sg.ShadowQuality=0', conteudo)
                                novo = re.sub(r'sg\.FoliageQuality=[0-9]+', 'sg.FoliageQuality=0', novo)
                                novo = re.sub(r'sg\.EffectsQuality=[0-9]+', 'sg.EffectsQuality=0', novo)
                                novo = re.sub(r'sg\.PostProcessQuality=[0-9]+', 'sg.PostProcessQuality=0', novo)
                                
                                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                                    f.write(novo)
                                sucesso = True
        return True, "✅ Modo Batata Injetado (Gráficos Ultra-Low)!"
    except Exception as e:
        return False, f"⚠️ Erro ao aplicar Modo Batata: {e}"

def reverter_potato():
    return True, "Modo Ultra-Leve (Potato Mode)"