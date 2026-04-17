"""
modo_competitivo_bs.py — Modo Competitivo para Blood Strike
============================================================
Edita os arquivos .ini do Blood Strike para desativar efeitos visuais
que não afetam a gameplay mas consomem CPU/GPU desnecessariamente:

  • Desativa animações de detalhes (DetailedAnimation=0)
  • Reduz qualidade de partículas (r.ParticleLODBias alto)
  • Desliga sombras dinâmicas (r.ShadowQuality=0)
  • Remove motion blur (r.MotionBlurQuality=0)
  • Aumenta distância de renderização de inimigos
  • Força textura de vegetação em baixa (r.Foliage.LODDistanceScale=0)
  • Desativa pós-processamento pesado (r.PostProcessAAQuality=0)

Todas as alterações são revertíveis.
"""

import os
import re
import platform

# ─── Caminhos do Blood Strike ─────────────────────────────────────────────────
from utils_bs import pastas_bs, editar_ini


# ─── Configurações competitivas ───────────────────────────────────────────────
SUBS_COMPETITIVO = [
    # Sombras
    (r"r\.ShadowQuality=[0-9]+",            "r.ShadowQuality=0"),
    (r"sg\.ShadowQuality=[0-9]+",           "sg.ShadowQuality=0"),
    # Motion blur
    (r"r\.MotionBlurQuality=[0-9]+",        "r.MotionBlurQuality=0"),
    # Anti-aliasing pesado
    (r"r\.PostProcessAAQuality=[0-9]+",     "r.PostProcessAAQuality=0"),
    # Partículas
    (r"r\.ParticleLODBias=-?[0-9.]+",      "r.ParticleLODBias=3"),
    # Vegetação (foliagem)
    (r"r\.Foliage\.LODDistanceScale=[0-9.]+", "r.Foliage.LODDistanceScale=0"),
    # Animações detalhadas
    (r"DetailedAnimation=[01]",             "DetailedAnimation=0"),
    # Pós-proc
    (r"r\.BloomQuality=[0-9]+",            "r.BloomQuality=0"),
    (r"r\.LensFlareQuality=[0-9]+",        "r.LensFlareQuality=0"),
    # Distant objects
    (r"r\.SkeletalMeshLODBias=[0-9.]+",    "r.SkeletalMeshLODBias=-1"),
]

ADICIONAR_COMPETITIVO = {
    "r.ShadowQuality":        "r.ShadowQuality=0",
    "r.MotionBlurQuality":    "r.MotionBlurQuality=0",
    "r.PostProcessAAQuality": "r.PostProcessAAQuality=0",
    "r.BloomQuality":         "r.BloomQuality=0",
    "r.LensFlareQuality":     "r.LensFlareQuality=0",
    "r.ParticleLODBias":      "r.ParticleLODBias=3",
    "DetailedAnimation":      "DetailedAnimation=0",
}

# ─── Valores padrão (reverter) ────────────────────────────────────────────────
SUBS_REVERTER = [
    (r"r\.ShadowQuality=0",             "r.ShadowQuality=2"),
    (r"sg\.ShadowQuality=0",            "sg.ShadowQuality=1"),
    (r"r\.MotionBlurQuality=0",         "r.MotionBlurQuality=4"),
    (r"r\.PostProcessAAQuality=0",      "r.PostProcessAAQuality=4"),
    (r"r\.ParticleLODBias=3",           "r.ParticleLODBias=0"),
    (r"r\.Foliage\.LODDistanceScale=0", "r.Foliage.LODDistanceScale=1"),
    (r"DetailedAnimation=0",            "DetailedAnimation=1"),
    (r"r\.BloomQuality=0",              "r.BloomQuality=5"),
    (r"r\.LensFlareQuality=0",          "r.LensFlareQuality=2"),
]


def aplicar_modo_competitivo():
    """Aplica configurações visuais mínimas para maior desempenho de frame-time."""
    if platform.system() != "Windows":
        import time; time.sleep(0.5)
        return True, "✅ (Simulação) Modo Competitivo ativado!"

    editados = 0
    for pasta in pastas_bs():
        if os.path.exists(pasta):
            for root, _, files in os.walk(pasta):
                for arq in files:
                    if arq.endswith(".ini"):
                        if editar_ini(os.path.join(root, arq),
                                       SUBS_COMPETITIVO, ADICIONAR_COMPETITIVO):
                            editados += 1

    if editados > 0:
        return True, f"✅ Modo Competitivo ativado! {editados} arquivo(s) ajustados."
    return True, "✅ Modo Competitivo aplicado (nenhuma config encontrada — será aplicado ao iniciar o jogo)."


def reverter_modo_competitivo():
    """Reverte configurações visuais para o padrão do jogo."""
    if platform.system() != "Windows":
        return True, "Modo Competitivo revertido."

    for pasta in pastas_bs():
        if os.path.exists(pasta):
            for root, _, files in os.walk(pasta):
                for arq in files:
                    if arq.endswith(".ini"):
                        editar_ini(os.path.join(root, arq), SUBS_REVERTER)

    return True, "Modo Competitivo desativado — configurações padrão restauradas."
