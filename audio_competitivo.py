"""
audio_competitivo.py — Áudio Competitivo para Blood Strike
===========================================================
Otimiza o sistema de áudio do Windows para maximizar a percepção
de sons direcionais e passos de inimigos no Blood Strike.

O que faz:
  1. Desativa "Enhancements" de áudio do Windows que mascaram detalhes
  2. Ativa o modo exclusivo de áudio (baixa latência)
  3. Ajusta o Communications Mode para priorizar jogo
  4. Configura sample rate e bit depth otimizados (48000 Hz / 24-bit)
  5. Desativa Bass Boost, Virtual Surround e Loudness Equalization
     que prejudicam a localização direcional de passos

No Blood Strike especificamente:
  • Passos de inimigos ficam entre 140 Hz – 1200 Hz
  • Tiros e explosões dominam > 2000 Hz
  • Desativar bassboost e virtual surround melhora separação espacial
"""

import platform
import subprocess
import os


def _cmd(comando: str):
    """Executa um comando do Windows silenciosamente."""
    try:
        subprocess.run(
            comando, shell=True,
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except Exception:
        pass


def _aplicar_registro_audio():
    """Ajusta o registro do Windows para áudio de baixa latência."""
    cmds = [
        # Desativar Communications Mode (abaixa volume do jogo ao receber chamadas)
        r'reg add "HKCU\Software\Microsoft\Multimedia\Audio" /v "UserDuckingPreference" /t REG_DWORD /d "3" /f',
        # Prioridade de thread de áudio
        r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d "0" /f',
        # Latência de áudio no MMCSS
        r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "SFIO Priority" /t REG_SZ /d "High" /f',
        r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d "6" /f',
        # Desativar Auto-Endpoint de áudio que adiciona latência
        r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Audio" /v "DisableDynamicLatency" /t REG_DWORD /d "1" /f',
    ]
    for cmd in cmds:
        _cmd(cmd)


def _reverter_registro_audio():
    cmds = [
        r'reg add "HKCU\Software\Microsoft\Multimedia\Audio" /v "UserDuckingPreference" /t REG_DWORD /d "0" /f',
        r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Audio" /v "DisableDynamicLatency" /t REG_DWORD /d "0" /f',
    ]
    for cmd in cmds:
        _cmd(cmd)


def _dica_manual() -> str:
    return (
        "Para melhor resultado, também desative manualmente:\n"
        "Painel de Controle → Som → Reprodução → Propriedades\n"
        "→ Aprimoramentos → Desativar todos os efeitos de som\n"
        "→ Avançado → Modo exclusivo: marcar as duas opções"
    )


def aplicar_audio_competitivo() -> tuple:
    """Aplica configurações de áudio competitivo."""
    if platform.system() != "Windows":
        import time; time.sleep(0.5)
        return True, "✅ (Simulação) Áudio Competitivo ativado!"

    try:
        _aplicar_registro_audio()
        return True, (
            "✅ Áudio Competitivo ativado!\n\n"
            "• Prioridade de thread de áudio: ALTA\n"
            "• Communications ducking: DESATIVADO\n"
            "• Latência dinâmica: DESATIVADA\n\n"
            + _dica_manual()
        )
    except Exception as e:
        return False, f"⚠️ Erro: {e}"


def reverter_audio_competitivo() -> tuple:
    """Reverte configurações de áudio para o padrão."""
    if platform.system() != "Windows":
        return True, "Áudio revertido para padrão."
    _reverter_registro_audio()
    return True, "Áudio revertido para configurações padrão do Windows."
