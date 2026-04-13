import platform
import subprocess

def otimizar_carregamento():
    """Otimiza a leitura de disco e expande o cache de shaders/mapas."""
    if platform.system() != "Windows":
        import time; time.sleep(1.5)
        return True, "✅ (Simulação Linux) Carregamento Turbo Ativado!"
    
    try:
        comandos = [
            # 1. Impede o Windows de enviar o núcleo do sistema para o HD, libertando o disco para ler apenas o jogo
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "DisablePagingExecutive" /t REG_DWORD /d "1" /f',
            
            # 2. Força o Windows a usar a RAM extra para armazenar ficheiros de mapas em cache
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "LargeSystemCache" /t REG_DWORD /d "1" /f',
            
            # 3. Tweak para NVIDIA: Aumenta o OGL Shader Cache para 10GB (Se não tiver NVIDIA, o Windows ignora sem dar erro)
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\nvlddmkm\\Global\\NVTweak" /v "OglShaderCacheSpace" /t REG_DWORD /d "10737418240" /f'
        ]
        
        for cmd in comandos:
            subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        return True, "✅ Carregamento Turbo (Mapas e Shaders) Ativado!"
    except Exception as e:
        return False, f"⚠️ Erro ao otimizar carregamento: {e}"

def reverter_carregamento():
    """Volta as configurações de disco e RAM para o padrão da Microsoft."""
    if platform.system() != "Windows": 
        return True, "Carregamento Turbo de Mapas (Shader Cache)"
    
    try:
        comandos = [
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "DisablePagingExecutive" /t REG_DWORD /d "0" /f',
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "LargeSystemCache" /t REG_DWORD /d "0" /f'
        ]
        for cmd in comandos:
            subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True, "Carregamento Turbo de Mapas (Shader Cache)"
    except: 
        return False, "Carregamento Turbo de Mapas (Shader Cache)"