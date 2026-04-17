"""
bs_server_ping.py — Seletor e medidor de latência dos servidores Blood Strike
==============================================================================
Pinga os IPs conhecidos dos servidores NetEase do Blood Strike e indica
qual região oferece o menor ping para o jogador.

Regiões suportadas:
  • SA  — América do Sul (Brasil, Argentina)
  • NA  — América do Norte (EUA, Canadá)
  • EU  — Europa (Frankfurt, Amsterdam)
  • AS  — Ásia (Singapura, Tokyo)
  • ME  — Oriente Médio (Dubai)

NOTA: Sem injeção no processo do jogo. Apenas ICMP ping simples.
"""

import platform
import subprocess
import threading
import time

# ─── IPs dos endpoints NetEase / Blood Strike por região ──────────────────────
SERVIDORES_BS = {
    "🇧🇷 SA - Brasil":       ["45.250.141.1",  "47.128.10.1",   "gs1-sa.bloodstrike.com"],
    "🌎 SA - Latam":         ["13.228.1.1",    "52.77.248.1",   "gs2-sa.bloodstrike.com"],
    "🇺🇸 NA - EUA":          ["54.236.1.1",    "3.236.1.1",     "gs-na.bloodstrike.com"],
    "🇩🇪 EU - Europa":       ["18.184.1.1",    "52.29.1.1",     "gs-eu.bloodstrike.com"],
    "🇸🇬 AS - Singapura":    ["47.128.1.1",    "13.229.1.1",    "gs-as.bloodstrike.com"],
    "🇯🇵 AS - Japão":        ["54.249.1.1",    "52.196.1.1",    "gs-jp.bloodstrike.com"],
}

# Servidores de fallback (CDN NetEase conhecidos)
FALLBACK_HOSTS = {
    "🇧🇷 SA - Brasil":    "gameserver-br.g.netease.com",
    "🌎 SA - Latam":      "gameserver-la.g.netease.com",
    "🇺🇸 NA - EUA":       "gameserver-na.g.netease.com",
    "🇩🇪 EU - Europa":    "gameserver-eu.g.netease.com",
    "🇸🇬 AS - Singapura": "gameserver-sg.g.netease.com",
    "🇯🇵 AS - Japão":     "gameserver-jp.g.netease.com",
}

# ─── Estado global ────────────────────────────────────────────────────────────
_resultados = {}
_monitorando = False
_thread_monitor = None
_callback_atualizacao = None


def _ping_host(host: str, tentativas: int = 4) -> float:
    """Retorna a média de ping em ms para um host. Retorna 9999.0 se inacessível."""
    sistema = platform.system()
    pings = []

    for _ in range(tentativas):
        try:
            if sistema == "Windows":
                cmd = ["ping", "-n", "1", "-w", "1500", host]
                saida = subprocess.check_output(cmd, stderr=subprocess.DEVNULL,
                                                creationflags=subprocess.CREATE_NO_WINDOW,
                                                timeout=3).decode(errors="ignore")
                for linha in saida.splitlines():
                    if "ms" in linha.lower():
                        for part in linha.split():
                            if "ms" in part:
                                val = ''.join(c for c in part if c.isdigit() or c == '.')
                                if val:
                                    pings.append(float(val))
                                    break
            else:
                # Linux / macOS
                cmd = ["ping", "-c", "1", "-W", "2", host]
                saida = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=3).decode(errors="ignore")
                for linha in saida.splitlines():
                    if "time=" in linha.lower():
                        val = linha.lower().split("time=")[-1].split()[0].replace("ms", "")
                        if val:
                            pings.append(float(val))
        except Exception:
            pass
        time.sleep(0.1)

    return round(sum(pings) / len(pings), 1) if pings else 9999.0


def _medir_regiao(nome_regiao: str):
    """Mede o ping de todos os IPs de uma região e retorna o melhor."""
    ips = SERVIDORES_BS.get(nome_regiao, [])
    fallback = FALLBACK_HOSTS.get(nome_regiao, "")

    melhor = 9999.0
    for ip in ips:
        p = _ping_host(ip, tentativas=2)
        if p < melhor:
            melhor = p

    # Tenta fallback CDN se os IPs diretos falharam
    if melhor == 9999.0 and fallback:
        melhor = _ping_host(fallback, tentativas=3)

    return melhor


def medir_todos_servidores(callback=None) -> dict:
    """
    Mede o ping de todos os servidores em paralelo.
    Se callback for fornecido, chama callback(resultados_parciais) a cada região medida.
    Retorna dicionário {região: ping_ms}.
    """
    global _resultados
    _resultados = {}
    lock = threading.Lock()

    def _medir_e_notificar(nome):
        ping = _medir_regiao(nome)
        with lock:
            _resultados[nome] = ping
        if callback:
            try:
                callback(dict(_resultados))
            except Exception:
                pass

    threads = [threading.Thread(target=_medir_e_notificar, args=(nome,), daemon=True)
               for nome in SERVIDORES_BS]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=8)

    return dict(_resultados)


def melhor_servidor() -> tuple[str, float]:
    """Retorna (nome_regiao, ping_ms) do servidor com menor latência."""
    if not _resultados:
        medir_todos_servidores()
    if not _resultados:
        return ("Desconhecido", 9999.0)
    melhor = min(_resultados, key=lambda k: _resultados[k])
    return (melhor, _resultados[melhor])


def iniciar_monitoramento_continuo(intervalo_segundos: int = 60, callback=None):
    """
    Inicia medição periódica em background.
    callback(resultados) é chamado após cada rodada.
    """
    global _monitorando, _thread_monitor, _callback_atualizacao
    _monitorando = True
    _callback_atualizacao = callback

    def _loop():
        while _monitorando:
            medir_todos_servidores(callback=_callback_atualizacao)
            for _ in range(intervalo_segundos * 10):
                if not _monitorando:
                    break
                time.sleep(0.1)

    _thread_monitor = threading.Thread(target=_loop, daemon=True)
    _thread_monitor.start()


def parar_monitoramento():
    global _monitorando
    _monitorando = False


def obter_resultados() -> dict:
    """Retorna os resultados mais recentes (cache)."""
    return dict(_resultados)
