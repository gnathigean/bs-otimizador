import os
import re
import platform

def pastas_bs():
    """Retorna a lista de pastas de configuração conhecidas do Blood Strike no Windows."""
    if platform.system() != "Windows":
        return []
    appdata   = os.environ.get("LOCALAPPDATA", "")
    locallow  = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow")
    documentos = os.path.join(os.environ.get("USERPROFILE", ""), "Documents")
    return [
        os.path.join(appdata,    "NetEase", "BloodStrike", "Saved", "Config", "WindowsNoEditor"),
        os.path.join(locallow,   "NetEase", "BloodStrike", "Saved", "Config", "WindowsNoEditor"),
        os.path.join(documentos, "BloodStrike", "Config"),
        os.path.join(appdata,    "NetEase", "BloodStrike"),
    ]

def editar_ini(caminho, substituicoes_regex, adicionar_se_ausente=None):
    """Lê um arquivo .ini, aplica substituições regex e acrescenta linhas ausentes."""
    try:
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            conteudo = f.read()

        novo = conteudo
        for padrao, valor in substituicoes_regex:
            novo = re.sub(padrao, valor, novo)

        if adicionar_se_ausente:
            for chave, linha in adicionar_se_ausente.items():
                if chave not in novo:
                    novo += f"\n{linha}"

        if novo != conteudo:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(novo)
            return True
    except Exception:
        pass
    return False
