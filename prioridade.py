import platform
import psutil

def definir_prioridade_alta():
    """Procura o processo do Blood Strike e força a prioridade para ALTA no processador."""
    
    # Proteção para simular no seu Linux sem dar erro
    if platform.system() != "Windows":
        import time
        time.sleep(1) # Simula o delay de busca
        return True, "✅ (Simulação Linux) Blood Strike em Prioridade Alta!"

    # Nomes comuns do executável do Blood Strike no Windows
    jogos_alvo = ["blood strike.exe", "bloodstrike.exe", "client.exe", "project_x.exe"]
    encontrou_jogo = False

    try:
        # Vasculha todos os programas abertos no PC
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and proc.info['name'].lower() in jogos_alvo:
                # Se achou o jogo, muda a prioridade do Windows para HIGH (Alta)
                proc.nice(psutil.HIGH_PRIORITY_CLASS)
                encontrou_jogo = True
        
        if encontrou_jogo:
            return True, "✅ Blood Strike com 100% de foco da CPU!"
        else:
            return False, "⚠️ Jogo não encontrado. Abra o Blood Strike primeiro!"
            
    except psutil.AccessDenied:
        return False, "⚠️ Sem permissão. Execute o Otimizador como Administrador!"
    except Exception as e:
        return False, f"⚠️ Erro ao otimizar: {e}"

def reverter_prioridade():
    """Volta o jogo para a prioridade Normal (caso o usuário desligue o switch)."""
    if platform.system() != "Windows":
        return True, "Impulsionar Blood Strike (Prioridade CPU)"

    jogos_alvo = ["blood strike.exe", "bloodstrike.exe", "client.exe", "project_x.exe"]
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and proc.info['name'].lower() in jogos_alvo:
                # Volta para prioridade padrão (NORMAL)
                proc.nice(psutil.NORMAL_PRIORITY_CLASS)
        return True, "Impulsionar Blood Strike (Prioridade CPU)"
    except:
        return False, "Impulsionar Blood Strike (Prioridade CPU)"