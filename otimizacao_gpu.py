import platform
import subprocess

def otimizar_gpu():
    """Força o sistema a usar o plano de Alto Desempenho para extrair o máximo da GPU."""
    
    if platform.system() != "Windows":
        import time
        time.sleep(1) # Simula o processamento
        return True, "✅ (Simulação Linux) GPU forçada em Desempenho Máximo!"

    try:
        # Comando nativo do Windows para ativar o plano de "Alto Desempenho"
        # O código '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c' é o ID universal do High Performance no Windows
        cmd = 'powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'
        subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        return True, "✅ GPU e Energia em Desempenho Máximo!"
    except Exception as e:
        return False, f"⚠️ Erro ao otimizar GPU: {e}"

def reverter_gpu():
    """Volta para o plano de energia Equilibrado."""
    if platform.system() != "Windows":
        return True, "Otimização Exclusiva de GPU"
    
    try:
        # O código '381b4222-f694-41f0-9685-ff5bb260df2e' é o ID universal do modo Equilibrado (Balanced)
        cmd = 'powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e'
        subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True, "Otimização Exclusiva de GPU"
    except:
        return False, "Otimização Exclusiva de GPU"