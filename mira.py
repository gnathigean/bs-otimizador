import platform
import threading
import tkinter as tk

janela_mira = None
cor_atual = "#00E676"
modelo_atual = "padrão"
overlay_rodando = False

def iniciar_overlay():
    global janela_mira, cor_atual, modelo_atual, overlay_rodando
    
    if janela_mira and janela_mira.winfo_exists():
        janela_mira.destroy()
        
    janela_mira = tk.Toplevel()
    janela_mira.overrideredirect(True)
    janela_mira.wm_attributes("-topmost", True)
    
    tamanho = 40 
    
    if platform.system() == "Windows":
        janela_mira.wm_attributes("-transparentcolor", "black")
        janela_mira.configure(bg="black")
        bg_color = "black"
    else:
        janela_mira.configure(bg="gray10")
        bg_color = "gray10"

    largura_tela = janela_mira.winfo_screenwidth()
    altura_tela = janela_mira.winfo_screenheight()
    pos_x = (largura_tela // 2) - (tamanho // 2)
    pos_y = (altura_tela // 2) - (tamanho // 2)
    
    janela_mira.geometry(f"{tamanho}x{tamanho}+{pos_x}+{pos_y}")
    canvas = tk.Canvas(janela_mira, width=tamanho, height=tamanho, bg=bg_color, highlightthickness=0, bd=0, relief="flat")
    canvas.pack(fill="both", expand=True)

    def desenhar():
        canvas.delete("all")
        mid = tamanho // 2
        
        if modelo_atual == "ponto":
            canvas.create_oval(mid-2, mid-2, mid+2, mid+2, fill=cor_atual, outline=cor_atual)
        elif modelo_atual == "pequeno":
            canvas.create_line(mid-5, mid, mid+5, mid, fill=cor_atual, width=2)
            canvas.create_line(mid, mid-5, mid, mid+5, fill=cor_atual, width=2)
        else: # padrão
            canvas.create_line(mid-10, mid, mid+10, mid, fill=cor_atual, width=2)
            canvas.create_line(mid, mid-10, mid, mid+10, fill=cor_atual, width=2)
            canvas.create_oval(mid-1, mid-1, mid+1, mid+1, fill="red", outline="red")

    def verificar_atualizacoes():
        global overlay_rodando
        if not overlay_rodando:
            janela_mira.destroy()
            return
        desenhar()
        janela_mira.after(200, verificar_atualizacoes) 

    desenhar()
    janela_mira.after(200, verificar_atualizacoes)

def ativar_mira(cor, modelo="padrão"):
    global cor_atual, modelo_atual, overlay_rodando
    cor_atual = cor
    modelo_atual = modelo
    if not overlay_rodando:
        overlay_rodando = True
        iniciar_overlay()

def desativar_mira():
    global overlay_rodando, janela_mira
    overlay_rodando = False
    if janela_mira and janela_mira.winfo_exists():
        janela_mira.destroy()
        janela_mira = None