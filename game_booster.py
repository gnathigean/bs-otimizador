import platform
import psutil
import time

def ativar_booster():
    """Mata processos pesados e em segundo plano de forma segura."""
    if platform.system() != "Windows":
        time.sleep(1)
        return "✅ (Simulação) 4 aplicações pesadas encerradas!"
    
    alvos = ['chrome.exe', 'msedge.exe', 'discord.exe', 'epicgameslauncher.exe', 'steamwebhelper.exe', 'brave.exe']
    mortos = 0
    
    try:
        for proc in psutil.process_iter(['name']):
            try:
                nome_processo = proc.info.get('name')
                if nome_processo and nome_processo.lower() in alvos:
                    proc.kill()
                    mortos += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Se não conseguir matar um programa específico, apenas ignora e vai para o próximo!
                continue
                
        return f"✅ Game Booster: {mortos} processos pesados encerrados!"
    except Exception as e:
        return f"⚠️ Erro no Booster: {e}"