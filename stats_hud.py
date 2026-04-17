"""
stats_hud.py — Overlay de estatísticas de partida para Blood Strike
=====================================================================
Exibe um HUD arrastável e transparente com:
  • Contador de Kills, Headshots e Mortes
  • Ratio K/D e HS% calculados em tempo real
  • Cronômetro de sessão (tempo de partida ao vivo)
  • Histórico das últimas 5 partidas (salvo em JSON local)
  • Hotkeys globais configuráveis pelo usuário (padrão: F5/F6/F7/F8)
  • Tentativa de leitura passiva de log do BS para detecção automática

Hotkeys padrão (configuráveis via set_hotkeys()):
  F5  → +1 Kill
  F6  → +1 Headshot
  F7  → +1 Morte
  F8  → Reset da partida

Sem injeção de memória — apenas leitura de arquivo de log.
"""

import tkinter as tk
import threading
import platform
import time
import os
import json
from datetime import datetime

# ─── Estado global ─────────────────────────────────────────────────────────────
_stats = {"kills": 0, "hs": 0, "mortes": 0}
_hud_app = None
_hud_thread = None
_rodando = False
_hotkeys_thread = None
_hotkeys_ativas = False
_log_thread = None
_log_ativo = False

# Cronômetro
_tempo_inicio_sessao = None
_partida_ativa = False

# Hotkeys configuráveis (códigos VK Windows)
_hotkeys_config = {
    "kill":   0x74,  # F5
    "hs":     0x75,  # F6
    "morte":  0x76,  # F7
    "reset":  0x77,  # F8
}

# Arquivo de histórico
_ARQUIVO_HISTORICO = os.path.join(
    os.path.expanduser("~"), "BS_Optimizer_Backups", "stats_historico.json"
)


# ─── Histórico de partidas ────────────────────────────────────────────────────

def _garantir_pasta_historico():
    os.makedirs(os.path.dirname(_ARQUIVO_HISTORICO), exist_ok=True)


def _carregar_historico() -> list:
    try:
        _garantir_pasta_historico()
        if os.path.exists(_ARQUIVO_HISTORICO):
            with open(_ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []


def _salvar_historico(historico: list):
    try:
        _garantir_pasta_historico()
        with open(_ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
            json.dump(historico[-10:], f, indent=2, ensure_ascii=False)  # mantém últimas 10
    except Exception:
        pass


def _registrar_partida(kills, hs, mortes, duracao_s):
    """Salva a partida encerrada no histórico."""
    kd = f"{kills / mortes:.2f}" if mortes > 0 else f"{kills}.0"
    hspct = f"{hs / kills * 100:.0f}%" if kills > 0 else "0%"
    mins = int(duracao_s // 60)
    segs = int(duracao_s % 60)
    historico = _carregar_historico()
    historico.append({
        "data":     datetime.now().strftime("%d/%m %H:%M"),
        "kills":    kills,
        "hs":       hs,
        "mortes":   mortes,
        "kd":       kd,
        "hs_pct":   hspct,
        "duracao":  f"{mins:02d}:{segs:02d}",
    })
    _salvar_historico(historico)
    return historico


def obter_historico() -> list:
    return _carregar_historico()


def exportar_historico_csv() -> str:
    """Exporta o histórico para CSV. Retorna o caminho do arquivo."""
    historico = _carregar_historico()
    if not historico:
        return ""
    pasta = os.path.join(os.path.expanduser("~"), "BS_Optimizer_Backups")
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, f"bs_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("Data,Kills,HS,Mortes,K/D,HS%,Duração\n")
        for p in historico:
            f.write(f"{p['data']},{p['kills']},{p['hs']},{p['mortes']},{p['kd']},{p['hs_pct']},{p['duracao']}\n")
    return caminho


# ─── Cálculos ──────────────────────────────────────────────────────────────────

def _calcular_kd():
    d = _stats["mortes"]
    k = _stats["kills"]
    if d == 0:
        return f"{k}.0" if k > 0 else "0.0"
    return f"{k / d:.2f}"


def _calcular_hs_pct():
    k = _stats["kills"]
    if k == 0:
        return "0%"
    return f"{(_stats['hs'] / k * 100):.0f}%"


def _tempo_sessao_str():
    if _tempo_inicio_sessao is None:
        return "00:00"
    elapsed = time.time() - _tempo_inicio_sessao
    mins = int(elapsed // 60)
    segs = int(elapsed % 60)
    return f"{mins:02d}:{segs:02d}"


# ─── Leitura passiva de log do BS (sem injeção) ────────────────────────────────

def _pastas_log_bs():
    if platform.system() != "Windows":
        return []
    appdata  = os.environ.get("LOCALAPPDATA", "")
    locallow = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow")
    return [
        os.path.join(appdata,  "NetEase", "BloodStrike", "Saved", "Logs"),
        os.path.join(locallow, "NetEase", "BloodStrike", "Saved", "Logs"),
    ]


def _encontrar_log_bs():
    for pasta in _pastas_log_bs():
        if os.path.exists(pasta):
            logs = [f for f in os.listdir(pasta) if f.endswith(".log")]
            if logs:
                return os.path.join(pasta, sorted(logs)[-1])
    return None


def _loop_leitura_log():
    """
    Leitura passiva do arquivo de log do BS.
    Detecta eventos de Kill e Morte via padrões de texto.
    Sem injeção de memória — 100% seguro.
    """
    global _log_ativo
    log_path = _encontrar_log_bs()
    if not log_path:
        return

    posicao = 0
    # Padrões conhecidos nos logs do Unreal Engine / Blood Strike
    PADROES_KILL  = ["KillConfirmed", "EliminatedPlayer", "YouKilledEnemy", "KillEvent"]
    PADROES_MORTE = ["YouDied", "PlayerEliminated", "RespawnEvent", "DeathEvent"]

    while _log_ativo:
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(posicao)
                linhas = f.readlines()
                posicao = f.tell()

            for linha in linhas:
                for p in PADROES_KILL:
                    if p in linha:
                        if _hud_app and _hud_app.winfo_exists():
                            _hud_app.incrementar("kills")
                        break
                for p in PADROES_MORTE:
                    if p in linha:
                        if _hud_app and _hud_app.winfo_exists():
                            _hud_app.incrementar("mortes")
                        break
        except Exception:
            pass
        time.sleep(0.5)


# ==============================================================================
# JANELA DO HUD
# ==============================================================================

class StatsHUD(tk.Toplevel):
    """Overlay flutuante de estatísticas de partida — versão 2.0 com cronômetro."""

    def __init__(self):
        super().__init__()

        self.title("BS Stats")
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        if platform.system() == "Windows":
            self.attributes("-transparentcolor", "#0a0a0f")
        self.configure(bg="#0a0a0f")

        self._x = 0
        self._y = 0

        # Posiciona no canto superior direito da tela
        larg_tela = self.winfo_screenwidth()
        self.geometry(f"210x260+{larg_tela - 225}+20")

        # ── Container principal ───────────────────────────────────────────────
        outer = tk.Frame(self, bg="#12121a", bd=2, relief="groove")
        outer.pack(fill="both", expand=True, padx=2, pady=2)

        # Cabeçalho com título + cronômetro
        header = tk.Frame(outer, bg="#1a0a2e")
        header.pack(fill="x", padx=2, pady=(4, 0))
        tk.Label(
            header, text="⚡ BS STATS", bg="#1a0a2e",
            fg="#8b5cf6", font=("Impact", 12)
        ).pack(side="left", padx=8, pady=4)
        self.lbl_timer = tk.Label(
            header, text="⏱ 00:00", bg="#1a0a2e",
            fg="#00e5ff", font=("Consolas", 10, "bold")
        )
        self.lbl_timer.pack(side="right", padx=8, pady=4)

        # ── Grid de stats ──────────────────────────────────────────────────────
        grid = tk.Frame(outer, bg="#12121a")
        grid.pack(padx=10, pady=4)

        self.lbl_kills  = self._label_stat(grid, "Kills",   "#00e676", 0)
        self.lbl_hs     = self._label_stat(grid, "HS",      "#d500f9", 1)
        self.lbl_mortes = self._label_stat(grid, "Mortes",  "#ff3a3a", 2)
        self.lbl_kd     = self._label_stat(grid, "K/D",     "#00e5ff", 3)
        self.lbl_hspct  = self._label_stat(grid, "HS%",     "#ff6d00", 4)

        self._atualizar_labels()

        # ── Separador ─────────────────────────────────────────────────────────
        tk.Frame(outer, bg="#2a2a3e", height=1).pack(fill="x", padx=5, pady=3)

        # ── Botões de + rápido ─────────────────────────────────────────────────
        btn_frame = tk.Frame(outer, bg="#12121a")
        btn_frame.pack(pady=(2, 2))

        self._btn(btn_frame, "+Kill  F5", "#00e676",  lambda: self._add("kills"),  0)
        self._btn(btn_frame, "+HS    F6", "#d500f9",  lambda: self._add("hs"),     1)
        self._btn(btn_frame, "+Morte F7", "#ff3a3a",  lambda: self._add("mortes"), 2)
        self._btn(btn_frame, "↺ Reset F8", "#666688", self._reset, 3)

        # ── Dica ──────────────────────────────────────────────────────────────
        tk.Label(
            outer, text="Duplo-clique: fechar",
            bg="#12121a", fg="#444466", font=("Consolas", 7)
        ).pack(pady=(2, 4))

        # ── Arrastar ──────────────────────────────────────────────────────────
        for widget in (outer, grid, btn_frame, header):
            widget.bind("<ButtonPress-1>",   self._iniciar_arrasto)
            widget.bind("<B1-Motion>",       self._arrastar)
        self.bind("<ButtonPress-1>",   self._iniciar_arrasto)
        self.bind("<B1-Motion>",       self._arrastar)
        self.bind("<Double-Button-1>", lambda e: self._fechar())

        # Tick do cronômetro
        self._tick_timer()

    # ── Helpers de UI ──────────────────────────────────────────────────────────

    def _label_stat(self, parent, titulo, cor, linha):
        tk.Label(parent, text=f"{titulo}:", bg="#12121a",
                 fg="#94a3b8", font=("Consolas", 10), anchor="w", width=7
                 ).grid(row=linha, column=0, sticky="w", pady=1)
        lbl = tk.Label(parent, text="0", bg="#12121a",
                       fg=cor, font=("Consolas", 11, "bold"), anchor="e", width=7)
        lbl.grid(row=linha, column=1, sticky="e", pady=1)
        return lbl

    def _btn(self, parent, texto, cor, cmd, linha):
        tk.Button(
            parent, text=texto, bg="#1e1e2e", fg=cor,
            font=("Consolas", 9, "bold"), relief="flat", bd=0,
            activebackground="#2a2a3e", activeforeground=cor,
            cursor="hand2", command=cmd, width=14
        ).grid(row=linha, column=0, pady=1, sticky="ew", padx=4)

    # ── Lógica de contagem ────────────────────────────────────────────────────

    def _add(self, chave):
        global _partida_ativa, _tempo_inicio_sessao
        _stats[chave] += 1
        # Inicia o cronômetro no primeiro evento da partida
        if not _partida_ativa:
            _partida_ativa = True
            _tempo_inicio_sessao = time.time()
        self._atualizar_labels()

    def _reset(self):
        global _partida_ativa, _tempo_inicio_sessao
        # Salva no histórico antes de resetar
        if _partida_ativa or any(v > 0 for v in _stats.values()):
            duracao = (time.time() - _tempo_inicio_sessao) if _tempo_inicio_sessao else 0
            _registrar_partida(_stats["kills"], _stats["hs"], _stats["mortes"], duracao)

        _stats["kills"] = 0
        _stats["hs"] = 0
        _stats["mortes"] = 0
        _partida_ativa = False
        _tempo_inicio_sessao = None
        self._atualizar_labels()
        self.lbl_timer.config(text="⏱ 00:00")

    def _atualizar_labels(self):
        if not self.winfo_exists():
            return
        self.lbl_kills.config(text=str(_stats["kills"]))
        self.lbl_hs.config(text=str(_stats["hs"]))
        self.lbl_mortes.config(text=str(_stats["mortes"]))
        self.lbl_kd.config(text=_calcular_kd())
        self.lbl_hspct.config(text=_calcular_hs_pct())

    def _tick_timer(self):
        """Atualiza o cronômetro a cada segundo."""
        if not self.winfo_exists():
            return
        try:
            self.lbl_timer.config(text=f"⏱ {_tempo_sessao_str()}")
        except Exception:
            pass
        self.after(1000, self._tick_timer)

    # Thread-safe
    def incrementar(self, chave):
        self.after(0, lambda: self._add(chave))

    def resetar(self):
        self.after(0, self._reset)

    # ── Arrastar ──────────────────────────────────────────────────────────────

    def _iniciar_arrasto(self, event):
        self._x = event.x
        self._y = event.y

    def _arrastar(self, event):
        dx = event.x - self._x
        dy = event.y - self._y
        self.geometry(f"+{self.winfo_x() + dx}+{self.winfo_y() + dy}")

    # ── Fechar ────────────────────────────────────────────────────────────────

    def _fechar(self):
        global _rodando, _hud_app, _partida_ativa
        _rodando = False
        _hud_app = None
        _partida_ativa = False
        self.destroy()


# ==============================================================================
# HOTKEYS GLOBAIS CONFIGURÁVEIS
# ==============================================================================

def set_hotkeys(kill_vk: int = None, hs_vk: int = None,
                morte_vk: int = None, reset_vk: int = None):
    """
    Configura os codes VK das hotkeys globais.
    Exemplo: set_hotkeys(kill_vk=0x74) para manter F5 no kill.
    Códigos VK comuns: F1=0x70, F2=0x71 ... F12=0x7B
    """
    if kill_vk  is not None: _hotkeys_config["kill"]  = kill_vk
    if hs_vk    is not None: _hotkeys_config["hs"]    = hs_vk
    if morte_vk is not None: _hotkeys_config["morte"] = morte_vk
    if reset_vk is not None: _hotkeys_config["reset"] = reset_vk


def _loop_hotkeys():
    """Polling de teclas de função. Usa ctypes no Windows."""
    global _hotkeys_ativas
    try:
        import ctypes
        GetAsyncKeyState = ctypes.windll.user32.GetAsyncKeyState

        estados = {k: False for k in _hotkeys_config}

        while _hotkeys_ativas:
            for acao, codigo in _hotkeys_config.items():
                pressionado = bool(GetAsyncKeyState(codigo) & 0x8000)
                if pressionado and not estados[acao]:
                    if _hud_app and _hud_app.winfo_exists():
                        if acao == "kill":
                            _hud_app.incrementar("kills")
                        elif acao == "hs":
                            _hud_app.incrementar("hs")
                        elif acao == "morte":
                            _hud_app.incrementar("mortes")
                        elif acao == "reset":
                            _hud_app.resetar()
                estados[acao] = pressionado
            time.sleep(0.05)
    except Exception:
        pass


# ==============================================================================
# FUNÇÕES PÚBLICAS
# ==============================================================================

def ativar_stats_hud():
    """Inicia o HUD de estatísticas em thread dedicada."""
    global _hud_thread, _hud_app, _rodando, _hotkeys_thread, _hotkeys_ativas
    global _log_thread, _log_ativo, _partida_ativa, _tempo_inicio_sessao

    if _rodando and _hud_app and _hud_app.winfo_exists():
        return True, "HUD de Stats já está ativo!"

    _rodando = True
    _partida_ativa = False
    _tempo_inicio_sessao = None
    _stats["kills"] = 0
    _stats["hs"] = 0
    _stats["mortes"] = 0

    if _hud_app and _hud_app.winfo_exists():
        _hud_app.destroy()

    _hud_app = StatsHUD()

    # Hotkeys globais
    _hotkeys_ativas = True
    _hotkeys_thread = threading.Thread(target=_loop_hotkeys, daemon=True)
    _hotkeys_thread.start()

    # Leitura de log (tenta, não bloqueia se não encontrar)
    _log_ativo = True
    _log_thread = threading.Thread(target=_loop_leitura_log, daemon=True)
    _log_thread.start()

    return True, "✅ HUD de Stats Ativado! Use F5/F6/F7/F8 para contar."


def fechar_stats_hud():
    """Fecha o HUD de estatísticas de forma thread-safe."""
    global _hud_app, _rodando, _hotkeys_ativas, _log_ativo
    _rodando = False
    _hotkeys_ativas = False
    _log_ativo = False
    if _hud_app is not None:
        try:
            if _hud_app.winfo_exists():
                _hud_app.destroy()
        except Exception:
            pass
        _hud_app = None
    return False, "HUD de Stats Desativado."


def esta_ativo() -> bool:
    return _rodando and _hud_app is not None


def obter_stats() -> dict:
    """Retorna cópia dos stats atuais para uso externo."""
    return dict(_stats)


def obter_tempo_sessao() -> str:
    """Retorna o tempo da sessão atual formatado."""
    return _tempo_sessao_str()
