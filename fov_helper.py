"""
fov_helper.py — Ajuste de Campo de Visão (FOV) para Blood Strike
================================================================
Edita o valor FOV diretamente no arquivo de configuração do BS.

No Blood Strike (Unreal Engine), o FOV base é 70°. Jogadores competitivos
geralmente usam valores entre 80°–100° para maior consciência espacial.

Valores recomendados:
  • 70°  — Padrão do jogo (mais zoom, menor área visível)
  • 85°  — Levemente mais aberto (mais contexto sem distorção)
  • 90°  — Equilíbrio competitivo popular
  • 100° — Mais campo de visão (detecta flancos mais cedo)
  • 110° — Máximo prático sem distorção excessiva
"""

import os
import re
import platform

from utils_bs import pastas_bs


def _aplicar_fov_arquivo(caminho: str, fov: int) -> bool:
    try:
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            conteudo = f.read()

        novo = conteudo
        # GameUserSettings.ini — chave padrão
        novo = re.sub(r"FieldOfView=[0-9.]+", f"FieldOfView={float(fov):.6f}", novo)
        novo = re.sub(r"FOVAngle=[0-9.]+",    f"FOVAngle={float(fov):.6f}",     novo)
        # Engine.ini — override de FOV
        novo = re.sub(r"r\.DefaultFeature\.FieldOfView=[0-9.]+",
                      f"r.DefaultFeature.FieldOfView={fov}", novo)

        if "FieldOfView" not in novo:
            novo += f"\nFieldOfView={float(fov):.6f}\n"

        if novo != conteudo:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(novo)
            return True
    except Exception:
        pass
    return False


def aplicar_fov(fov: int) -> tuple:
    """
    Define o FOV do Blood Strike.
    fov: valor em graus (recomendado 70–110).
    """
    fov = max(60, min(120, int(fov)))  # limite seguro

    if platform.system() != "Windows":
        import time; time.sleep(0.3)
        return True, f"✅ (Simulação) FOV ajustado para {fov}°"

    editados = 0
    for pasta in pastas_bs():
        if os.path.exists(pasta):
            for root, _, files in os.walk(pasta):
                for arq in files:
                    if arq.lower() in ("gameusersettings.ini", "engine.ini", "input.ini"):
                        if _aplicar_fov_arquivo(os.path.join(root, arq), fov):
                            editados += 1

    return True, f"✅ FOV ajustado para {fov}° ({editados} arquivo(s) editados)."


def reverter_fov() -> tuple:
    """Reverte FOV para o padrão do Blood Strike (70°)."""
    return aplicar_fov(70)


FOV_PRESETS = {
    "Padrão (70°)":        70,
    "Leve+ (85°)":         85,
    "Competitivo (90°)":   90,
    "Amplo (100°)":        100,
    "Máximo (110°)":       110,
}
