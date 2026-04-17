import platform
import subprocess

def ajustar_mmcss_mouse():
    """Ajusta o Win32PrioritySeparation e o MMCSS para focar na renderização de hardware e resposta do mouse."""
    if platform.system() != "Windows":
        import time; time.sleep(1)
        return True, "✅ (Simulação Linux) Input Lag Remover ativado!"
    
    try:
        comandos = [
            # Win32PrioritySeparation ajusta a prioridade dada às tarefas de primeiro plano (o jogo)
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl" /v "Win32PrioritySeparation" /t REG_DWORD /d "38" /f',
            
            # Otimização específica do perfil "Games" no Windows MMCSS (Multimedia Class Scheduler)
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "GPU Priority" /t REG_DWORD /d "8" /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "Priority" /t REG_DWORD /d "6" /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "Scheduling Category" /t REG_SZ /d "High" /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "SFIO Priority" /t REG_SZ /d "High" /f',
            
            # Melhora a latência geral de USB / Dispositivos
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "LargeSystemCache" /t REG_DWORD /d "0" /f'
        ]
        
        for cmd in comandos:
            subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        return True, "✅ Input Lag Aniquilado: Resposta bruta do Teclado/Mouse ativada!"
    except Exception as e:
        return False, f"⚠️ Erro no MMCSS: {e}"

def reverter_mmcss():
    if platform.system() != "Windows": return True, "Delay 0 Teclado/Mouse (MMCSS)"
    try:
        comandos = [
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl" /v "Win32PrioritySeparation" /t REG_DWORD /d "2" /f'
        ]
        for cmd in comandos:
            subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True, "Delay 0 Teclado/Mouse (MMCSS)"
    except: return False, "Delay 0 Teclado/Mouse (MMCSS)"
