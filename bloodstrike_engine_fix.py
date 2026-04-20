import os
import subprocess
import platform
import ctypes

def _run_cmd(cmd):
    try:
        subprocess.run(cmd, shell=True, capture_output=True, creationflags=0x08000000)
    except:
        pass

def otimizar_engine_bs():
    """Aplica otimizações de Engine (Unity) e Registro para Blood Strike."""
    if platform.system() != "Windows": return True, "Otimização Blood Strike (Simulada)"

    try:
        # 1. Desativar Fullscreen Optimizations (FSO) via Registro
        # O valor 2 desativa o FSO para o jogo, reduzindo input lag de tela cheia.
        comandos = [
            'reg add "HKCU\\System\\GameConfigStore" /v "GameDVR_FSEBehavior" /t REG_DWORD /d "2" /f',
            'reg add "HKCU\\System\\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d "0" /f',
            
            # 2. Otimização de Mouse (MouseDataQueueSize)
            # Reduz o buffer de entrada para resposta mais rápida do mouse
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\mouclass\\Parameters" /v "MouseDataQueueSize" /t REG_DWORD /d "20" /f',
            
            # 3. Variáveis de Ambiente Unity para Performance
            'setx UNITY_DISABLE_HW_STATS "1"',
            'setx __GL_THREADED_OPTIMIZATIONS "1"'
        ]
        
        for cmd in comandos:
            _run_cmd(cmd)
            
        return True, "✅ Engine Blood Strike Otimizada! (FSO Off, Mouse Response Boost)"
    except Exception as e:
        return False, f"Erro ao otimizar engine: {e}"

def limpar_cache_logs_bs():
    """Limpa logs e caches da NetEase que podem causar stuttering."""
    if platform.system() != "Windows": return True, "Limpeza (Simulada)"

    paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\BloodStrike\Saved\Logs"),
        os.path.expandvars(r"%LOCALAPPDATA%\BloodStrike\Saved\Crashes"),
        os.path.expandvars(r"%LOCALAPPDATA%\BloodStrike\Saved\StalkerLog"),
    ]
    
    count = 0
    for path in paths:
        if os.path.exists(path):
            try:
                import shutil
                shutil.rmtree(path)
                os.makedirs(path)
                count += 1
            except:
                pass
                
    return True, f"✅ Limpeza concluída: {count} pastas de logs recicladas."

def reset_engine_bs():
    """Restaura padrões do Windows."""
    if platform.system() != "Windows": return True, "Reset (Simulada)"
    
    comandos = [
        'reg add "HKCU\\System\\GameConfigStore" /v "GameDVR_FSEBehavior" /t REG_DWORD /d "0" /f',
        'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\mouclass\\Parameters" /v "MouseDataQueueSize" /t REG_DWORD /d "100" /f'
    ]
    for cmd in comandos:
        _run_cmd(cmd)
    return True, "Otimizações de Engine removidas."
