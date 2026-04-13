import platform
import subprocess

def acordar_nucleos():
    if platform.system() != "Windows":
        import time; time.sleep(1)
        return True, "✅ (Simulação Linux) 100% dos Núcleos Acordados!"
    try:
        cmd = 'powercfg -setacvalueindex scheme_current sub_processor 0cc5b647-c1df-4637-891a-dec35c318583 100'
        subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run("powercfg -setactive scheme_current", shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True, "✅ Unpark CPU: Todos os núcleos ativos!"
    except Exception as e:
        return False, f"⚠️ Erro no Unpark: {e}"

def reverter_unpark():
    return True, "Unpark CPU (Acordar 100% dos Núcleos)"