"""
bs_config_backup.py — Backup e Restauro de Configurações do Blood Strike
=========================================================================
Cria um arquivo .zip com todos os arquivos .ini do Blood Strike,
permitindo restaurar rapidamente em caso de:
  • Atualizações do jogo que resetam configurações
  • Problemas após otimizações
  • Mudança de computador
  • Compartilhamento de configurações entre amigos

O backup inclui:
  • Todos os arquivos .ini da pasta Config
  • GameUserSettings.ini (configurações de gráficos e controles)
  • Engine.ini (otimizações de FPS e qualidade)
  • Input.ini (mapeamento de teclas)
"""

import os
import platform
import zipfile
import shutil
from datetime import datetime
import subprocess

# ─── Diretório de backups ─────────────────────────────────────────────────────
def _dir_backup():
    base = os.path.join(os.path.expanduser("~"), "BS_Optimizer_Backups")
    os.makedirs(base, exist_ok=True)
    return base


from utils_bs import pastas_bs


def criar_backup(nome_descritivo: str = "") -> tuple:
    """
    Cria um arquivo .zip com todas as configs do Blood Strike.
    Retorna (sucesso: bool, mensagem: str, caminho_zip: str|None).
    """
    if platform.system() != "Windows":
        import time; time.sleep(0.8)
        return True, "✅ (Simulação) Backup criado!", None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sufixo = f"_{nome_descritivo.replace(' ', '_')}" if nome_descritivo else ""
    nome_arquivo = f"BS_Config_{timestamp}{sufixo}.zip"
    caminho_zip = os.path.join(_dir_backup(), nome_arquivo)

    arquivos_adicionados = 0
    try:
        with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for pasta in pastas_bs():
                if not os.path.exists(pasta):
                    continue
                for root, _, files in os.walk(pasta):
                    for arq in files:
                        if arq.endswith((".ini", ".cfg", ".json")):
                            caminho_arq = os.path.join(root, arq)
                            # Nome relativo dentro do zip
                            arcname = os.path.relpath(caminho_arq, os.path.dirname(pasta))
                            zf.write(caminho_arq, arcname)
                            arquivos_adicionados += 1

        if arquivos_adicionados == 0:
            os.remove(caminho_zip)
            return False, "⚠️ Nenhum arquivo de configuração do Blood Strike encontrado.\nVerifique se o jogo já foi executado ao menos uma vez.", None

        return True, (
            f"✅ Backup criado com sucesso!\n\n"
            f"📂 {arquivos_adicionados} arquivo(s) salvo(s)\n"
            f"💾 Local: {caminho_zip}"
        ), caminho_zip

    except Exception as e:
        return False, f"⚠️ Erro ao criar backup: {e}", None


def listar_backups() -> list[dict]:
    """Retorna lista de backups disponíveis com metadados."""
    dir_back = _dir_backup()
    backups = []
    for arq in os.listdir(dir_back):
        if arq.endswith(".zip") and arq.startswith("BS_Config_"):
            caminho = os.path.join(dir_back, arq)
            stat = os.stat(caminho)
            backups.append({
                "nome":     arq,
                "caminho":  caminho,
                "tamanho":  f"{stat.st_size / 1024:.1f} KB",
                "data":     datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M"),
            })
    return sorted(backups, key=lambda x: x["data"], reverse=True)


def restaurar_backup(caminho_zip: str) -> tuple:
    """
    Restaura as configurações a partir de um arquivo .zip de backup.
    """
    if platform.system() != "Windows":
        return True, "✅ (Simulação) Backup restaurado!"

    if not os.path.exists(caminho_zip):
        return False, "⚠️ Arquivo de backup não encontrado."

    try:
        # Pasta temporária de extração
        tmp = os.path.join(_dir_backup(), "_temp_restore")
        if os.path.exists(tmp):
            shutil.rmtree(tmp)
        os.makedirs(tmp)

        with zipfile.ZipFile(caminho_zip, "r") as zf:
            zf.extractall(tmp)

        restaurados = 0
        for pasta_bs in pastas_bs():
            if os.path.exists(pasta_bs):
                for root, _, files in os.walk(tmp):
                    for arq in files:
                        if arq.endswith(".ini"):
                            src = os.path.join(root, arq)
                            dst = os.path.join(pasta_bs, arq)
                            try:
                                shutil.copy2(src, dst)
                                restaurados += 1
                            except Exception:
                                pass

        shutil.rmtree(tmp, ignore_errors=True)

        if restaurados == 0:
            return False, "⚠️ Nenhum arquivo pôde ser restaurado (verifique permissões)."
        return True, f"✅ {restaurados} arquivo(s) restaurado(s) com sucesso!"

    except Exception as e:
        return False, f"⚠️ Erro ao restaurar backup: {e}"


def abrir_pasta_backup():
    """Abre a pasta de backups no Explorer."""
    dir_back = _dir_backup()
    if platform.system() == "Windows":
        os.startfile(dir_back)
    elif platform.system() == "Darwin":
        subprocess.run(["open", dir_back])
    else:
        subprocess.run(["xdg-open", dir_back])
