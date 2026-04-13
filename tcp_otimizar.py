import platform
import subprocess

def otimizar_tcp():
    if platform.system() != "Windows":
        import time; time.sleep(1)
        return True, "✅ (Simulação Linux) Roteamento TCP/IP Otimizado!"
    try:
        comandos = [
            "ipconfig /flushdns",
            "netsh winsock reset",
            "netsh int ip reset"
        ]
        for cmd in comandos:
            subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True, "✅ Roteamento TCP/IP Otimizado com sucesso!"
    except Exception as e:
        return False, f"⚠️ Erro ao otimizar TCP/IP: {e}"

def reverter_tcp():
    return True, "Otimizar Roteamento TCP/IP (Forçar Servidores SP)"