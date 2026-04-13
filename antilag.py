import platform
import subprocess

def otimizar_fluidez():
    """Altera o registro do Windows para remover otimizações pesadas de tela cheia."""
    if platform.system() != "Windows":
        import time; time.sleep(1)
        return True, "✅ (Simulação Linux) Antilag ativado no Registro!"
    
    try:
        # Comandos para desligar o GameDVR e GameBar via CMD
        comandos = [
            'reg add "HKCU\\System\\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d "0" /f',
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\GameDVR" /v "AllowGameDVR" /t REG_DWORD /d "0" /f'
        ]
        for cmd in comandos:
            subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        return True, "✅ Fluidez Máxima: GameDVR e Input Lag removidos!"
    except Exception as e:
        return False, f"⚠️ Erro ao aplicar Antilag: {e}"

def reverter_fluidez():
    if platform.system() != "Windows": return True, "Fluidez Máxima (Antilag)"
    try:
        comandos = [
            'reg add "HKCU\\System\\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d "1" /f',
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\GameDVR" /v "AllowGameDVR" /t REG_DWORD /d "1" /f'
        ]
        for cmd in comandos:
            subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True, "Fluidez Máxima (Antilag)"
    except: return False, "Fluidez Máxima (Antilag)"