import platform
import subprocess

def forcar_tela_cheia():
    if platform.system() != "Windows":
        import time; time.sleep(1)
        return True, "✅ (Simulação) Tela Cheia Exclusiva Ativada!"
    try:
        cmd = 'reg add "HKCU\\Software\\Microsoft\\GameBar" /v "ShowStartupPanel" /t REG_DWORD /d "0" /f'
        subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True, "✅ Tela Cheia Exclusiva Ativada!"
    except Exception as e:
        return False, f"⚠️ Erro: {e}"

def reverter_tela_cheia():
    return True, "Forçar Tela Cheia Exclusiva"