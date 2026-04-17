import os
import shutil
import platform
import glob

def limpar_cache_bs():
    """Limpa Caches, Logs e Arquivos Temporários de jogo do Blood Strike."""
    if platform.system() != "Windows":
        return True, "✅ (Simulação) Cache do Blood Strike limpo!"

    appdata = os.environ.get('LOCALAPPDATA', '')
    locallow = os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'LocalLow')
    
    pastas_alvo = [
        os.path.join(appdata, 'NetEase', 'BloodStrike', 'Saved', 'Crashes'),
        os.path.join(appdata, 'NetEase', 'BloodStrike', 'Saved', 'Logs'),
        os.path.join(appdata, 'NetEase', 'BloodStrike', 'Saved', 'webcache'),
        os.path.join(locallow, 'NetEase', 'BloodStrike', 'Saved', 'Crashes'),
        os.path.join(locallow, 'NetEase', 'BloodStrike', 'Saved', 'Logs')
    ]
    
    arquivos_limpos = 0
    
    try:
        for pasta in pastas_alvo:
            if os.path.exists(pasta):
                for root, dirs, files in os.walk(pasta, topdown=False):
                    for name in files:
                        try:
                            os.remove(os.path.join(root, name))
                            arquivos_limpos += 1
                        except: pass
                    for name in dirs:
                        try:
                            os.rmdir(os.path.join(root, name))
                        except: pass
                        
        # Limpar D3D / Shaders DirectX (genérico mas foca no BS porque ele gera muito cache)
        temp_dir = os.environ.get('TEMP', '')
        if os.path.exists(temp_dir):
            for padrao in ['*.log', 'NVIDIA Corporation\\NV_Cache\\*']:
                for filepath in glob.glob(os.path.join(temp_dir, padrao), recursive=True):
                    try:
                        os.remove(filepath)
                        arquivos_limpos += 1
                    except: pass
                    
        return True, f"✅ Limpeza BS Concluída: {arquivos_limpos} Lixos removidos!"
    except Exception as e:
        return False, f"⚠️ Erro ao limpar cache interno do Blood Strike: {e}"

def reverter_limpeza_bs():
    return True, "Limpeza Profunda Blood Strike"
