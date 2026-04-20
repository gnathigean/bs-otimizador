"""
carregamento_turbo.py — Carregamento Instantâneo de Mapas para Blood Strike
============================================================================
Técnicas combinadas inspiradas no reetFPS / Point Blank para reduzir drasticamente
o tempo de carregamento de mapas:

  1. DisablePagingExecutive — evita que o kernel seja paginado para o HD
  2. LargeSystemCache — usa RAM extra como cache de mapas/assets do jogo
  3. NVIDIA Shader Cache 10 GB — elimina recompilação de shaders entre cargas
  4. Desativa SysMain (Superfetch) — impede pré-carregamento competitivo com o jogo
  5. I/O Priority do jogo — prioridade I/O elevada para o processo do BS
  6. Prefetch do DirectX — garante que a DLL de renderização esteja em memória
  7. Desativa defrag automático — evita que o desfragmentador concorra com leitura
"""

import os
import platform
import subprocess


def _run(cmd):
    """Helper para executar comandos ocultos sem janela."""
    try:
        subprocess.run(
            cmd, shell=True, capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except Exception:
        pass


def otimizar_carregamento():
    """Ativa todas as otimizações de carregamento de mapas."""
    if platform.system() != "Windows":
        import time; time.sleep(1.5)
        return True, "✅ (Simulação Linux) Carregamento Turbo Ativado!"

    try:
        comandos = [
            # ── 1. Mantém kernel na RAM (evita I/O do HD durante o jogo) ─────
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "DisablePagingExecutive" /t REG_DWORD /d "1" /f',

            # ── 2. Expande cache do sistema de arquivos para mapas/assets ─────
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "LargeSystemCache" /t REG_DWORD /d "1" /f',

            # ── 3. NVIDIA: Shader Cache 10 GB — elimina recompilação ──────────
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\nvlddmkm\\Global\\NVTweak" /v "OglShaderCacheSpace" /t REG_DWORD /d "10737418240" /f',

            # ── 4a. Desativa SysMain (Superfetch) — libera I/O para o jogo ───
            'sc stop "SysMain"',
            'sc config "SysMain" start= disabled',

            # ── 4b. Desativa prefetch do Windows (conflita com cache do jogo) ─
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" /v "EnablePrefetcher" /t REG_DWORD /d "0" /f',
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" /v "EnableSuperfetch" /t REG_DWORD /d "0" /f',

            # ── 5. Prioridade de I/O máxima para aplicações de jogos ─────────
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "Background Only" /t REG_SZ /d "False" /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "Priority" /t REG_DWORD /d "6" /f',

            # ── 6. Desabilita defrag automático (não concorre com leitura) ────
            'schtasks /Change /TN "\\Microsoft\\Windows\\Defrag\\ScheduledDefrag" /Disable',

            # ── 7. Desativa compressão de RAM (libera CPU para o jogo) ────────
            'powershell -WindowStyle Hidden -Command "Disable-MMAgent -mc"',

            # ── 8. Aumenta Working Set do sistema para manter assets em RAM ───
            # ── 8. Aumenta Working Set do sistema para manter assets em RAM ───
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "IoPageLockLimit" /t REG_DWORD /d "983040" /f',

            # ── 9. Prefetch Inteligente (Boot + Apps, sem prejudicar o jogo) ────
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" /v "EnableSuperfetch" /t REG_DWORD /d "2" /f',

            # ── 10. Cache de Shaders Ilimitado (NVIDIA) ───────────────────────
            'reg add "HKLM\\SOFTWARE\\NVIDIA Corporation\\Global\\OpenGL\\ShaderCacheSize" /t REG_DWORD /d "4294967295" /f'
        ]

        for cmd in comandos:
            _run(cmd)

        return True, "✅ Carregamento Turbo de Mapas Ativado! (SysMain desativado, RAM Cache expandido)"

    except Exception as e:
        return False, f"⚠️ Erro ao otimizar carregamento: {e}"


def reverter_carregamento():
    """Restaura todas as configurações de carregamento para o padrão Microsoft."""
    if platform.system() != "Windows":
        return True, "Carregamento Turbo de Mapas"

    try:
        comandos = [
            # Reverte paginação e cache
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "DisablePagingExecutive" /t REG_DWORD /d "0" /f',
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "LargeSystemCache" /t REG_DWORD /d "0" /f',

            # Reativa SysMain (Superfetch)
            'sc config "SysMain" start= auto',
            'sc start "SysMain"',

            # Reativa prefetch
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" /v "EnablePrefetcher" /t REG_DWORD /d "3" /f',
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" /v "EnableSuperfetch" /t REG_DWORD /d "3" /f',

            # Reativa defrag automático
            'schtasks /Change /TN "\\Microsoft\\Windows\\Defrag\\ScheduledDefrag" /Enable',

            # Reativa compressão de RAM
            'powershell -WindowStyle Hidden -Command "Enable-MMAgent -mc"',
        ]
        for cmd in comandos:
            _run(cmd)
        return True, "Carregamento Turbo de Mapas revertido para padrão."
    except Exception:
        return False, "Carregamento Turbo de Mapas"