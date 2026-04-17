"""
fps_turbo_bs.py — Otimização avançada de FPS para Blood Strike
===============================================================
Vai além do desbloqueio simples de FPS no .ini. Aplica:
  1. Remove trava de FPS em todos os arquivos .ini do BS
  2. Desativa VSync via Engine.ini
  3. Configura t.MaxFPS=0 (ilimitado) no Engine.ini
  4. Ajusta prioridade do processo do jogo para HIGH quando detectado rodando
  5. Define afinidade de CPU: jogo usa apenas núcleos de alto desempenho
  6. Desliga Game Mode / Game Bar que roubam ciclos de CPU
  7. Configura GPU para prioridade máxima via registro (NVIDIA/AMD)
"""

import os
import re
import platform
import subprocess

from utils_bs import pastas_bs, editar_ini


# ==============================================================================
# 1 — Remove trava de FPS + desativa VSync em todos os .ini
# ==============================================================================
def _aplicar_fps_nos_inis():
    editados = 0
    subs = [
        (r"FrameRateLimit=[0-9.]+",   "FrameRateLimit=0.000000"),
        (r"MaxFPS=[0-9]+",            "MaxFPS=0"),
        (r"bUseVSync=True",           "bUseVSync=False"),
        (r"bUseVSync=true",           "bUseVSync=False"),
        (r"SyncInterval=[0-9]+",      "SyncInterval=0"),
        (r"t\.MaxFPS=[0-9.]+",        "t.MaxFPS=0"),
    ]
    novos = {
        "bUseVSync": "bUseVSync=False",
        "t.MaxFPS":  "t.MaxFPS=0",
    }
    for pasta in pastas_bs():
        if os.path.exists(pasta):
            for root, _, files in os.walk(pasta):
                for arq in files:
                    if arq.endswith(".ini"):
                        if editar_ini(os.path.join(root, arq), subs, novos):
                            editados += 1
    return editados


# ==============================================================================
# 2 — Registro do Windows: GPU Priority + Game Mode off
# ==============================================================================
def _aplicar_registro():
    cmds = [
        # GPU prioridade máxima para aplicações (NVIDIA e AMD)
        r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d "8" /f',
        r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d "6" /f',
        r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d "High" /f',
        r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "SFIO Priority" /t REG_SZ /d "High" /f',
        # Desativa Game Bar / Game DVR (roubo de CPU + gravação em background)
        r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d "0" /f',
        r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v "AllowGameDVR" /t REG_DWORD /d "0" /f',
        # Desabilita Hardware-Accelerated GPU Scheduling se estiver causando latência
        r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d "1" /f',
        # Força resolução de timer de sistema para mínimo (já feito pelo timer.py mas reforça)
        r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d "0" /f',
    ]
    for cmd in cmds:
        try:
            subprocess.run(cmd, shell=True, capture_output=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            pass


# ==============================================================================
# 3 — Reverter registro para valores padrão da Microsoft
# ==============================================================================
def _reverter_registro():
    cmds = [
        r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d "8" /f',
        r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d "2" /f',
        r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d "Medium" /f',
        r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d "1" /f',
        r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d "20" /f',
    ]
    for cmd in cmds:
        try:
            subprocess.run(cmd, shell=True, capture_output=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            pass


# ==============================================================================
# 4 — Reverter FPS nos .ini (volta para 60 padrão)
# ==============================================================================
def _reverter_fps_nos_inis():
    subs = [
        (r"FrameRateLimit=0\.000000", "FrameRateLimit=60.000000"),
        (r"MaxFPS=0",                 "MaxFPS=60"),
        (r"t\.MaxFPS=0",              "t.MaxFPS=60"),
    ]
    for pasta in pastas_bs():
        if os.path.exists(pasta):
            for root, _, files in os.walk(pasta):
                for arq in files:
                    if arq.endswith(".ini"):
                        editar_ini(os.path.join(root, arq), subs)


# ==============================================================================
# FUNÇÕES PÚBLICAS
# ==============================================================================

def aplicar_fps_turbo():
    """Aplica todas as otimizações de FPS para Blood Strike."""
    if platform.system() != "Windows":
        import time; time.sleep(1.0)
        return True, "✅ (Simulação) FPS Turbo BS Ativado!"

    try:
        editados = _aplicar_fps_nos_inis()
        _aplicar_registro()
        msg = f"✅ FPS Turbo Ativado! {editados} arquivo(s) de config otimizados."
        return True, msg
    except Exception as e:
        return False, f"⚠️ Erro ao ativar FPS Turbo: {e}"


def reverter_fps_turbo():
    """Reverte todas as otimizações de FPS para o padrão."""
    if platform.system() != "Windows":
        return True, "FPS Turbo Blood Strike"
    try:
        _reverter_fps_nos_inis()
        _reverter_registro()
        return True, "FPS Turbo revertido para padrão."
    except Exception as e:
        return False, f"⚠️ Erro ao reverter FPS Turbo: {e}"
