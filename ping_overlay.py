import platform
import threading
import tkinter as tk
import dns_ping

janela_ping = None
overlay_rodando = False

def iniciar_overlay():
    global janela_ping, overlay_rodando
    janela_ping = tk.Tk()
    janela_ping.overrideredirect(True)
    janela_ping.wm_attributes("-topmost", True)
    
    if platform.system() == "Windows":
        janela_ping.wm_attributes("-transparentcolor", "black")
        janela_ping.configure(bg="black")
        bg_color = "black"
    else:
        janela_ping.configure(bg="gray10")
        bg_color = "gray10"
        
    # Posiciona no canto superior esquerdo
    janela_ping.geometry(f"130x40+20+20")
    
    lbl_ping = tk.Label(janela_ping, text="Ping: -- ms", font=("Arial", 14, "bold"), fg="#00E676", bg=bg_color)
    lbl_ping.pack(expand=True, fill="both")
    
    def atualizar():
        if not overlay_rodando:
            janela_ping.destroy()
            return
        try:
            ping = dns_ping.obter_ping_atual()
            cor = "#00E676" if ping < 50 else "#FF5252"
            lbl_ping.config(text=f"Ping: {ping} ms", fg=cor)
        except: pass
        janela_ping.after(2000, atualizar)
        
    janela_ping.after(100, atualizar)
    janela_ping.mainloop()

def ativar_ping():
    global overlay_rodando
    if not overlay_rodando:
        overlay_rodando = True
        threading.Thread(target=iniciar_overlay, daemon=True).start()
        return True, "✅ Overlay de Ping Ativado!"
    return True, "✅ Overlay já está rodando!"

def desativar_ping():
    global overlay_rodando
    overlay_rodando = False
    return True, "Monitor de Ping na Tela (Overlay in-game)"