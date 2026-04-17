import tkinter as tk
import psutil
import threading
import time
import platform

# ==============================================================================
# OVERLAY DE HARDWARE - Reescrito com tkinter puro para evitar conflito de
# mainloop com o CustomTkinter da janela principal. Destruição thread-safe via
# overlay_app.after(0, overlay_app.destroy) garante que o Tk processa o comando
# no próprio thead do evento, eliminando o deadlock ao desativar.
# ==============================================================================

_overlay_thread = None
_overlay_app = None
_rodando = False


class HardwareOverlay(tk.Toplevel):
    """Janela de overlay flutuante para monitoramento de CPU e RAM."""

    def __init__(self):
        super().__init__()

        self.title("BS Tracker")
        self.geometry("185x100+20+20")
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # No Windows usa transparência real; no Linux usa fundo escuro
        if platform.system() == "Windows":
            self.attributes("-transparentcolor", "#0a0a0f")
            self.configure(bg="#0a0a0f")
            bg = "#0a0a0f"
        else:
            self.configure(bg="#0a0a0f")
            bg = "#0a0a0f"

        # ── Estrutura visual ──────────────────────────────────────────────────
        frame = tk.Frame(self, bg="#12121a", bd=1, relief="solid")
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        tk.Label(
            frame, text="⚡ BS OPTIMIZER", bg="#12121a",
            fg="#8b5cf6", font=("Impact", 13)
        ).pack(pady=(6, 2))

        self.lbl_cpu = tk.Label(
            frame, text="CPU: --%", bg="#12121a",
            fg="#00e676", font=("Consolas", 12, "bold"), anchor="w"
        )
        self.lbl_cpu.pack(anchor="w", padx=14)

        self.lbl_ram = tk.Label(
            frame, text="RAM: --%", bg="#12121a",
            fg="#ff3a3a", font=("Consolas", 12, "bold"), anchor="w"
        )
        self.lbl_ram.pack(anchor="w", padx=14)

        tk.Label(
            frame, text="(duplo clique para fechar)", bg="#12121a",
            fg="#444455", font=("Arial", 8)
        ).pack(pady=(2, 5))

        # ── Binds de arrastar ─────────────────────────────────────────────────
        self.bind("<ButtonPress-1>", self._iniciar_arrasto)
        self.bind("<B1-Motion>", self._arrastar)
        self.bind("<Double-Button-1>", lambda e: self._fechar_seguro())

        self._x = 0
        self._y = 0
        self._after_id = None

        self._atualizar()

    # ── Lógica de dados ───────────────────────────────────────────────────────

    def _atualizar(self):
        """Atualiza CPU/RAM a cada 1 segundo enquanto a janela existir."""
        global _rodando
        if not _rodando:
            self._fechar_seguro()
            return

        if not self.winfo_exists():
            return
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            cor_cpu = "#00e676" if cpu < 80 else "#ff3a3a"
            cor_ram = "#00e676" if ram < 85 else "#ff3a3a"
            self.lbl_cpu.config(text=f"CPU: {cpu:.0f}%", fg=cor_cpu)
            self.lbl_ram.config(text=f"RAM: {ram:.0f}%", fg=cor_ram)
        except Exception:
            pass
        self._after_id = self.after(1000, self._atualizar)

    def _fechar_seguro(self):
        """Cancela o loop de atualização antes de destruir a janela."""
        global _rodando, _overlay_app
        _rodando = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        _overlay_app = None
        self.destroy()

    # ── Arrastar a janela ─────────────────────────────────────────────────────

    def _iniciar_arrasto(self, event):
        self._x = event.x
        self._y = event.y

    def _arrastar(self, event):
        dx = event.x - self._x
        dy = event.y - self._y
        self.geometry(f"+{self.winfo_x() + dx}+{self.winfo_y() + dy}")


# ==============================================================================
# FUNÇÕES PÚBLICAS — chamadas pelo main.py
# ==============================================================================

def ativar_overlay():
    """Inicia o overlay. Thread-safe."""
    global _overlay_app, _rodando

    if _rodando and _overlay_app and _overlay_app.winfo_exists():
        return True, "Overlay já está ativo!"

    _rodando = True
    _overlay_app = HardwareOverlay()
    
    return True, "Overlay de Hardware Ativado!"


def fechar_overlay():
    """Fecha o overlay de forma thread-safe."""
    global _rodando
    _rodando = False
    return False, "Overlay de Hardware Desativado."


def esta_ativo() -> bool:
    """Retorna True se o overlay está rodando."""
    return _rodando and _overlay_app is not None


# Compatibilidade retroativa com o nome antigo
def alternar_overlay():
    """Mantido para compatibilidade — use ativar_overlay / fechar_overlay."""
    if esta_ativo():
        return fechar_overlay()
    return ativar_overlay()