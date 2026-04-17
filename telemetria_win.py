import platform
import subprocess

def desativar_telemetria():
    """Desativa os serviços de telemetria do Xbox e Windows que devoram desempenho em segundo plano."""
    if platform.system() != "Windows":
        import time; time.sleep(1)
        return True, "✅ (Simulação Linux) Telemetria desativada!"
    
    try:
        comandos = [
            'sc stop DiagTrack',
            'sc config DiagTrack start= disabled',
            'sc stop dmwappushservice',
            'sc config dmwappushservice start= disabled',
            'schtasks /change /tn "Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator" /disable',
            'schtasks /change /tn "Microsoft\\Windows\\Customer Experience Improvement Program\\UsbCeip" /disable',
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v "AllowTelemetry" /t REG_DWORD /d "0" /f'
        ]
        
        for cmd in comandos:
            subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        return True, "✅ Telemetria Morta: Fim do spyware enviando dados pra MS!"
    except Exception as e:
        return False, f"⚠️ Erro ao bloquear Telemetria: {e}"

def reverter_telemetria():
    if platform.system() != "Windows": return True, "Bloquear Telemetria (Anti-Stutter)"
    try:
        comandos = [
            'sc config DiagTrack start= auto',
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v "AllowTelemetry" /t REG_DWORD /d "3" /f'
        ]
        for cmd in comandos:
            subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True, "Bloquear Telemetria (Anti-Stutter)"
    except: return False, "Bloquear Telemetria (Anti-Stutter)"
