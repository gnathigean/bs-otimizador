import platform
import subprocess

def otimizar_mouse():
    if platform.system() != "Windows":
        import time; time.sleep(1)
        return True, "✅ (Simulação Linux) Aceleração de mouse desativada!"
    try:
        comandos = [
            'reg add "HKCU\\Control Panel\\Mouse" /v "MouseSpeed" /t REG_SZ /d "0" /f',
            'reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold1" /t REG_SZ /d "0" /f',
            'reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold2" /t REG_SZ /d "0" /f'
        ]
        for cmd in comandos:
            subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True, "✅ Mira Bruta 1:1 (Aceleração do Windows Desativada)!"
    except Exception as e:
        return False, f"⚠️ Erro ao otimizar mouse: {e}"

def reverter_mouse():
    if platform.system() != "Windows": return True, "Mira Bruta 1:1 (Remover Aceleração do Windows)"
    try:
        subprocess.run('reg add "HKCU\\Control Panel\\Mouse" /v "MouseSpeed" /t REG_SZ /d "1" /f', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True, "Mira Bruta 1:1 (Remover Aceleração do Windows)"
    except: return False, "Mira Bruta 1:1 (Remover Aceleração do Windows)"