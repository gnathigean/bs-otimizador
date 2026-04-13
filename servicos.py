import platform
import subprocess

def otimizar_servicos():
    """Desativa serviços inúteis do Windows que consomem disco e CPU."""
    if platform.system() != "Windows":
        import time
        time.sleep(1)
        return True, "✅ (Simulação Linux) Serviços pesados desativados!"

    # Serviços alvos: SysMain (Superfetch), WSearch (Busca do Windows), DiagTrack (Telemetria)
    servicos_alvo = ["SysMain", "WSearch", "DiagTrack"]
    
    try:
        for servico in servicos_alvo:
            # Comando 1: Para o serviço imediatamente
            subprocess.run(["sc", "stop", servico], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            # Comando 2: Impede o serviço de iniciar sozinho de novo
            subprocess.run(["sc", "config", servico, "start=", "disabled"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        return True, "✅ Serviços inúteis desativados com sucesso!"
    except Exception as e:
        return False, f"⚠️ Erro! Execute o Otimizador como Administrador. ({e})"

def reverter_servicos():
    """Reativa os serviços caso o usuário desligue a chave."""
    if platform.system() != "Windows":
        return True, "Desativar Serviços Inúteis (Superfetch/Search)"

    servicos_alvo = ["SysMain", "WSearch", "DiagTrack"]
    try:
        for servico in servicos_alvo:
            subprocess.run(["sc", "config", servico, "start=", "auto"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(["sc", "start", servico], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True, "Desativar Serviços Inúteis (Superfetch/Search)"
    except:
        return False, "Desativar Serviços Inúteis (Superfetch/Search)"