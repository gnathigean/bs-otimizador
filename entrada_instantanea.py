import os
import platform

def otimizar_entrada():
    """Desativa os vídeos de introdução renomeando a extensão dos arquivos."""
    if platform.system() != "Windows":
        import time
        time.sleep(1) # Simula a varredura
        return True, "✅ (Simulação Linux) Telas de carregamento removidas!"

    # Possíveis diretórios do jogo (Steam e Launcher Padrão)
    pastas_jogo = [
        r"C:\Program Files (x86)\Steam\steamapps\common\Blood Strike",
        r"D:\SteamLibrary\steamapps\common\Blood Strike",
        r"C:\NetEase\BloodStrike",
        r"D:\NetEase\BloodStrike"
    ]
    
    sucesso_arquivos = 0
    jogo_achado = False

    try:
        for base_dir in pastas_jogo:
            if os.path.exists(base_dir):
                jogo_achado = True
                # Vasculha as pastas do jogo atrás de vídeos
                for root, dirs, files in os.walk(base_dir):
                    # Foca em pastas com 'video', 'movie' ou 'ui' para ser mais rápido
                    if 'video' in root.lower() or 'movie' in root.lower() or 'ui' in root.lower():
                        for file in files:
                            # Formatos comuns de intro
                            if file.endswith(('.mp4', '.webm', '.bk2')): 
                                old_path = os.path.join(root, file)
                                new_path = old_path + ".bak" # Oculta o arquivo do jogo
                                os.rename(old_path, new_path)
                                sucesso_arquivos += 1
                                
        if jogo_achado:
            return True, f"✅ Entrada Instantânea! ({sucesso_arquivos} vídeos pulados)"
        else:
            return False, "⚠️ Blood Strike não encontrado nos locais padrões."
            
    except Exception as e:
        return False, f"⚠️ Erro ao aplicar: {e}"

def reverter_entrada():
    """Restaura os vídeos de introdução caso o usuário desligue a chave."""
    if platform.system() != "Windows":
        return True, "Entrada Instantânea no Mapa"

    pastas_jogo = [
        r"C:\Program Files (x86)\Steam\steamapps\common\Blood Strike",
        r"D:\SteamLibrary\steamapps\common\Blood Strike",
        r"C:\NetEase\BloodStrike",
        r"D:\NetEase\BloodStrike"
    ]
    
    try:
        for base_dir in pastas_jogo:
            if os.path.exists(base_dir):
                for root, dirs, files in os.walk(base_dir):
                    if 'video' in root.lower() or 'movie' in root.lower() or 'ui' in root.lower():
                        for file in files:
                            if file.endswith('.bak'):
                                old_path = os.path.join(root, file)
                                # Remove a extensão '.bak' para voltar ao normal (mp4, webm...)
                                new_path = old_path[:-4] 
                                os.rename(old_path, new_path)
                                
        return True, "Entrada Instantânea no Mapa"
    except:
        return False, "Entrada Instantânea no Mapa"