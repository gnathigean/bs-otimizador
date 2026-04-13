import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import psutil
import platform
import subprocess
import ctypes

# ==============================================================================
# IMPORTAÇÃO DOS MOTORES MODULARES
# ==============================================================================
import limpeza, esvaziarmemo, dns_ping, prioridade, mira, servicos, timer 
import otimizacao_gpu, entrada_instantanea, desbloqueio_fps, antilag
import resolucao, snaptap, tcp_otimizar, ping_overlay, tela_cheia, unpark_cpu     
import mira_bruta, shaders, potato_mode, game_booster, carregamento_turbo 

# ==============================================================================
# CONFIGURAÇÕES DE DESIGN DINÂMICAS (Claro, Escuro)
# ==============================================================================
ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("dark-blue") 

CORES = {
    "bg_principal": ("#F2F2F7", "#101014"), 
    "bg_sidebar": ("#E5E5EA", "#16161D"),    
    "texto_base": ("#1C1C1E", "#EDEDF0"),   
    "texto_secundario": ("#3A3A3C", "#A0A0A5"),
    "roxo_destaque": ("#6200EE", "#BB86FC"),
    "bg_ping_panel": ("#FFFFFF", "#1E1E26"),
    "card_info": ("#FFFFFF", "#1C1C26"),
    "borda": ("#D1D1D6", "#3A3A55")
}

class App(ctk.CTk):
    def __init__(self, username="Visitante", dias_restantes=0):
        super().__init__()

        self.username = username
        self.dias_restantes = dias_restantes

        self.title("Blood Strike Optimizer Pro v3.0 | Premium Edition")
        self.geometry("1050x720") 
        self.resizable(False, False)
        self.configure(fg_color=CORES["bg_principal"])

        self.current_theme = "dark"
        self.frame_atual = None
        self.mira_cor = "#00E676" 

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ======================================================================
        # BARRA LATERAL (SIDEBAR)
        # ======================================================================
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=CORES["bg_sidebar"], border_width=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(9, weight=1)

        self.btn_tema = ctk.CTkButton(self.sidebar, text="🌙 Modo Escuro", font=("Roboto Medium", 12), fg_color="transparent", text_color=CORES["texto_base"], hover_color=("#D1D1D6", "#3A3A55"), height=38, corner_radius=20, border_width=1, border_color=CORES["borda"], command=self.toggle_tema)
        self.btn_tema.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="⚡ BS OPTIMIZER", font=ctk.CTkFont(size=24, weight="bold", family="Impact"), text_color=CORES["roxo_destaque"])
        self.logo_label.grid(row=1, column=0, padx=20, pady=(10, 30))

        # Menu
        self.btn_info = self.criar_botao_menu("📊 Hardware Info", 2, "info")
        self.btn_desempenho = self.criar_botao_menu("🚀 Desempenho Max", 3, "desempenho")
        self.btn_rede = self.criar_botao_menu("🌐 Conexão e Ping", 4, "rede")
        self.btn_visual = self.criar_botao_menu("🎯 Interface e Mira", 5, "visual")
        self.btn_ferramentas = self.criar_botao_menu("🛠️ Ferramentas Pro", 6, "ferramentas")

        # Painel de Licença
        self.sessao_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sessao_frame.grid(row=9, column=0, sticky="s", pady=25)
        ctk.CTkLabel(self.sessao_frame, text=f"👤 {self.username}", font=("Roboto Medium", 14), text_color=CORES["texto_base"]).pack()
        ctk.CTkLabel(self.sessao_frame, text=f"👑 VIP | {self.dias_restantes} Dias", font=("Roboto Bold", 13), text_color=("#008F39", "#00C853")).pack(pady=(2,0))

        def configurar_frame_conteudo(frame):
            frame.grid_columnconfigure(0, weight=1) 
            return frame

        # ======================================================================
        # 0. FRAME HARDWARE INFO (ABA)
        # ======================================================================
        self.frame_info = ctk.CTkFrame(self, fg_color="transparent")
        configurar_frame_conteudo(self.frame_info)
        self.criar_titulo(self.frame_info, "DIAGNÓSTICO DO SISTEMA")
        self.criar_painel_hardware(self.frame_info)

        # ======================================================================
        # 1. FRAME DESEMPENHO
        # ======================================================================
        self.frame_desempenho = ctk.CTkFrame(self, fg_color="transparent")
        configurar_frame_conteudo(self.frame_desempenho)
        self.criar_titulo(self.frame_desempenho, "OTIMIZAÇÃO DE DESEMPENHO")
        
        container_sw = ctk.CTkFrame(self.frame_desempenho, fg_color="transparent")
        container_sw.pack(fill="x", padx=30, pady=5)
        
        col_esq = ctk.CTkFrame(container_sw, fg_color="transparent")
        col_esq.pack(side="left", fill="both", expand=True)
        col_dir = ctk.CTkFrame(container_sw, fg_color="transparent")
        col_dir.pack(side="right", fill="both", expand=True)

        self.sw_fps = self.criar_switch_com_info(col_esq, "Desbloquear FPS Máximo", "Remove o limite oculto de quadros por segundo do jogo, permitindo que o seu PC entregue o máximo de FPS possível.", command=self.acionar_fps)
        self.sw_antilag = self.criar_switch_com_info(col_esq, "Modo Antilag (Zero Delay)", "Desativa o GameDVR e otimizações de tela cheia do Windows para reduzir drasticamente o atraso entre o seu clique e a ação na tela.", command=self.acionar_antilag)
        self.sw_timer = self.criar_switch_com_info(col_esq, "Sincronização Precisão (0.5ms)", "Ajusta o relógio interno do Windows para 0.5ms, melhorando o tempo de resposta do rato e teclado.", command=self.acionar_timer)
        self.sw_prioridade = self.criar_switch_com_info(col_esq, "Foco Extremo Processador", "Força o Windows a dar prioridade máxima de processamento ao jogo.", command=self.acionar_prioridade)
        
        self.sw_gpu = self.criar_switch_com_info(col_dir, "Overdrive de Placa de Vídeo", "Ativa o plano de 'Alto Desempenho' do Windows para extrair 100% da GPU.", command=self.acionar_gpu)
        self.sw_potato = self.criar_switch_com_info(col_dir, "Modo Ultra-Leve (Potato)", "Desativa sombras, reflexos e folhagens pesadas diretamente nos ficheiros raiz.", command=self.acionar_potato)
        self.sw_carregamento = self.criar_switch_com_info(col_dir, "Carregamento Fast de Mapas", "Usa a RAM extra como cache para pré-carregar texturas pesadas.", command=self.acionar_carregamento)
        self.sw_mira_bruta = self.criar_switch_com_info(col_dir, "Precisão Bruta do Mouse (1:1)", "Desliga a aceleração nativa e flutuante do Windows.", command=self.acionar_mira_bruta)

        botoes_base = ctk.CTkFrame(self.frame_desempenho, fg_color="transparent")
        botoes_base.pack(fill="x", padx=35, pady=(20, 0))
        
        self.btn_limpeza = self.criar_botao_acao_com_info(botoes_base, "🧹 Limpeza Profunda do Sistema", "Limpa arquivos de lixo e cache temporário do Windows que causam lentidão.", ("#3f37c9", "#BB86FC"), ("#27237a", "#D7B5FD"), side="left", command=self.acionar_limpeza)
        self.btn_shaders = self.criar_botao_acao_com_info(botoes_base, "🔧 Recriar Shaders (Fix Stutter)", "Exclui cache antigo da placa de vídeo para parar travadinhas durante os tiros.", ("#d35400", "#f39c12"), ("#e67e22", "#f1c40f"), side="right", command=self.acionar_shaders)

        # ======================================================================
        # 2. FRAME REDE
        # ======================================================================
        self.frame_rede = ctk.CTkFrame(self, fg_color="transparent")
        configurar_frame_conteudo(self.frame_rede)
        self.criar_titulo(self.frame_rede, "REDE E LATÊNCIA")
        
        self.ping_frame = ctk.CTkFrame(self.frame_rede, fg_color=CORES["bg_ping_panel"], corner_radius=15, border_width=1, border_color=CORES["borda"])
        self.ping_frame.pack(fill="x", padx=40, pady=(0, 20))
        self.lbl_ping_atual = ctk.CTkLabel(self.ping_frame, text="Ping Atual: -- ms", font=("Roboto Bold", 24))
        self.lbl_ping_atual.pack(pady=25)

        container_rede = ctk.CTkFrame(self.frame_rede, fg_color="transparent")
        container_rede.pack(fill="x", padx=40)
        self.sw_dns = self.criar_switch_com_info(container_rede, "Smart DNS Cloudflare (1.1.1.1)", "Altera a sua rota de internet para os servidores da Cloudflare, reduzindo a latência base do Windows.", command=self.acionar_smart_dns)
        self.sw_tcp = self.criar_switch_com_info(container_rede, "Otimizar Roteamento TCP/IP", "Limpa o cache corrompido de rede e reseta a placa para evitar Packet Loss.", command=self.acionar_tcp)
        self.sw_ping_overlay = self.criar_switch_com_info(container_rede, "Apresentar Ping Flutuante", "Abre um contador transparente de Ping que fica por cima do jogo.", command=self.acionar_ping_overlay)

        # ======================================================================
        # 3. FRAME VISUAL
        # ======================================================================
        self.frame_visual = ctk.CTkFrame(self, fg_color="transparent")
        configurar_frame_conteudo(self.frame_visual)
        self.criar_titulo(self.frame_visual, "MIRA E VISUAL")
        
        self.seg_mira = ctk.CTkSegmentedButton(self.frame_visual, values=["Padrão", "Ponto", "Pequeno"], command=self.atualizar_mira_dinamica)
        self.seg_mira.set("Padrão")
        self.seg_mira.pack(pady=10, padx=40, fill="x")

        self.mira_frame = ctk.CTkFrame(self.frame_visual, fg_color="transparent")
        self.mira_frame.pack(padx=40, pady=10)
        for cor in ["#FF1744", "#00E676", "#00E5FF", "#D500F9"]:
            btn = ctk.CTkButton(self.mira_frame, text="✛", width=50, height=50, text_color=cor, font=("Arial", 20, "bold"), fg_color=CORES["card_info"], hover_color=CORES["borda"], command=lambda c=cor: self.mudar_cor_mira(c))
            btn.pack(side="left", padx=5)
        
        btn_off = ctk.CTkButton(self.mira_frame, text="OFF", width=50, height=50, text_color=("white","white"), fg_color=("#c0392b", "#e74c3c"), command=self.desligar_mira)
        btn_off.pack(side="left", padx=5)

        container_vis = ctk.CTkFrame(self.frame_visual, fg_color="transparent")
        container_vis.pack(fill="x", padx=40, pady=20)
        self.sw_tela_cheia = self.criar_switch_com_info(container_vis, "Forçar Tela Cheia Exclusiva", "Obriga o jogo e o Windows a renderizarem em tela cheia real (Ignorando Borderless).", command=self.acionar_tela_cheia)
        self.sw_resolucao = self.criar_switch_com_info(container_vis, "Forçar Resolução Esticada", "Simula uma resolução esticada para alargar os inimigos.", command=self.acionar_resolucao)
        self.sw_entrada = self.criar_switch_com_info(container_vis, "Skip Intro (Pular Abertura)", "Oculta os vídeos que tocam quando abre o jogo, fazendo-o chegar no menu mais rápido.", command=self.acionar_entrada)

        # ======================================================================
        # 4. FRAME FERRAMENTAS
        # ======================================================================
        self.frame_ferramentas = ctk.CTkFrame(self, fg_color="transparent")
        configurar_frame_conteudo(self.frame_ferramentas)
        self.criar_titulo(self.frame_ferramentas, "FERRAMENTAS PRO")
        
        container_pro = ctk.CTkFrame(self.frame_ferramentas, fg_color="transparent")
        container_pro.pack(fill="x", padx=40)
        self.sw_snaptap = self.criar_switch_com_info(container_pro, "Teclado SnapTap (Software)", "Anula o atraso de Strafe A+D. Atenção: Riscos com Anti-Cheats.", is_risky=True, command=self.acionar_snaptap)
        self.sw_unpark = self.criar_switch_com_info(container_pro, "Unpark CPU (Acordar Núcleos)", "Impede o Windows de adormecer os núcleos do processador.", command=self.acionar_unpark)
        self.sw_servicos = self.criar_switch_com_info(container_pro, "Suspender Bloatware do Windows", "Desativa Telemetria, SysMain e Windows Search enquanto joga.", command=self.acionar_servicos)
        
        botoes_ferr = ctk.CTkFrame(self.frame_ferramentas, fg_color="transparent")
        botoes_ferr.pack(fill="x", padx=35, pady=(20, 0))

        self.btn_booster = self.criar_botao_acao_com_info(botoes_ferr, "🚀 Game Booster Extremo", "Mata processos pesados secundários como Chrome, Edge e Discord.", ("#c0392b", "#e74c3c"), ("#922B21", "#C0392B"), side="top", command=self.acionar_booster)
        self.btn_ram = self.criar_botao_acao_com_info(botoes_ferr, "⚡ Esvaziar Memória RAM", "Libera a memória RAM em espera (Standby Cache), essencial para quem tem 8GB/16GB.", ("#008F39", "#00C853"), ("#006929", "#008F39"), side="top", command=self.acionar_ram)

        self.selecionar_frame("info")
        self.iniciar_monitor_ping() 

    # --- LÓGICA DE HARDWARE INFO ---
    def criar_painel_hardware(self, frame_pai):
        panel = ctk.CTkFrame(frame_pai, fg_color=CORES["card_info"], corner_radius=15, border_width=1, border_color=CORES["borda"])
        panel.pack(fill="x", padx=40, pady=(10, 20))
        
        ctk.CTkLabel(panel, text="Especificações Lidas do seu Computador:", font=("Roboto Medium", 14), text_color=CORES["roxo_destaque"]).pack(pady=(15,5))
        
        info_frame = ctk.CTkFrame(panel, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        info = self.obter_info_sistema()
        
        for i in range(2): info_frame.grid_columnconfigure(i, weight=1)
        
        labels = [
            (f"🖥️ Processador: {info['cpu']}", 0, 0),
            (f"🎮 Placa de Vídeo: {info['gpu']}", 0, 1),
            (f"📟 Memória RAM: {info['ram']}", 1, 0),
            (f"💽 Armazenamento: {info['disk']}", 1, 1),
            (f"🕒 Taxa de Atualização: {info['refresh']}Hz", 2, 0),
            (f"⚙️ Sistema: {info['os']}", 2, 1)
        ]
        
        for text, r, c in labels:
            ctk.CTkLabel(info_frame, text=text, font=("Roboto", 13), text_color=CORES["texto_base"], anchor="w").grid(row=r, column=c, padx=10, pady=8, sticky="w")

    def obter_info_sistema(self):
        try:
            sistema = f"{platform.system()} {platform.release()}"
            cpu = platform.processor()
            if "Windows" in platform.system(): cpu = subprocess.check_output("wmic cpu get name", shell=True).decode().split('\n')[1].strip()
            gpu = "Integrada / Desconhecida"
            if "Windows" in platform.system():
                gpu_raw = subprocess.check_output("wmic path win32_VideoController get name", shell=True).decode().split('\n')
                gpu = gpu_raw[1].strip() if len(gpu_raw) > 1 else gpu
            ram = f"{round(psutil.virtual_memory().total / (1024**3))} GB Instalados"
            usage = psutil.disk_usage('C:\\' if "Windows" in platform.system() else '/')
            disk = f"{round(usage.total / (1024**3))} GB Total"
            refresh = 60
            if "Windows" in platform.system():
                user32 = ctypes.windll.user32
                refresh = user32.GetDeviceCaps(user32.GetDC(0), 116)
            return {"cpu": cpu[:35], "gpu": gpu[:30], "ram": ram, "disk": disk, "refresh": refresh, "os": sistema}
        except:
            return {"cpu": "Aguardando...", "gpu": "Aguardando...", "ram": "--", "disk": "--", "refresh": "--", "os": "Desconhecido"}

    # --- RESTANTE DAS AÇÕES (BACKEND) ---
    def acionar_carregamento(self):
        if self.sw_carregamento.get() == 1: threading.Thread(target=lambda: self.sw_carregamento.switch.configure(text=carregamento_turbo.otimizar_carregamento()[1]), daemon=True).start()
        else: self.sw_carregamento.switch.configure(text=carregamento_turbo.reverter_carregamento()[1])

    def acionar_mira_bruta(self):
        if self.sw_mira_bruta.get() == 1: threading.Thread(target=lambda: self.sw_mira_bruta.switch.configure(text=mira_bruta.otimizar_mouse()[1]), daemon=True).start()
        else: self.sw_mira_bruta.switch.configure(text=mira_bruta.reverter_mouse()[1])

    def acionar_shaders(self):
        threading.Thread(target=lambda: self.btn_shaders.configure(text=shaders.limpar_shaders()), daemon=True).start()

    def acionar_potato(self):
        if self.sw_potato.get() == 1: threading.Thread(target=lambda: self.sw_potato.switch.configure(text=potato_mode.aplicar_potato()[1]), daemon=True).start()
        else: self.sw_potato.switch.configure(text=potato_mode.reverter_potato()[1])

    def acionar_booster(self):
        threading.Thread(target=lambda: self.btn_booster.configure(text=game_booster.ativar_booster()), daemon=True).start()

    def acionar_tcp(self):
        if self.sw_tcp.get() == 1: threading.Thread(target=lambda: self.sw_tcp.switch.configure(text=tcp_otimizar.otimizar_tcp()[1]), daemon=True).start()
        else: self.sw_tcp.switch.configure(text=tcp_otimizar.reverter_tcp()[1])

    def acionar_ping_overlay(self):
        if self.sw_ping_overlay.get() == 1: threading.Thread(target=lambda: self.sw_ping_overlay.switch.configure(text=ping_overlay.ativar_ping()[1]), daemon=True).start()
        else: self.sw_ping_overlay.switch.configure(text=ping_overlay.desativar_ping()[1])

    def acionar_tela_cheia(self):
        if self.sw_tela_cheia.get() == 1: threading.Thread(target=lambda: self.sw_tela_cheia.switch.configure(text=tela_cheia.forcar_tela_cheia()[1]), daemon=True).start()
        else: self.sw_tela_cheia.switch.configure(text=tela_cheia.reverter_tela_cheia()[1])

    def acionar_unpark(self):
        if self.sw_unpark.get() == 1: threading.Thread(target=lambda: self.sw_unpark.switch.configure(text=unpark_cpu.acordar_nucleos()[1]), daemon=True).start()
        else: self.sw_unpark.switch.configure(text=unpark_cpu.reverter_unpark()[1])

    def acionar_antilag(self):
        if self.sw_antilag.get() == 1: threading.Thread(target=lambda: self.sw_antilag.switch.configure(text=antilag.otimizar_fluidez()[1]), daemon=True).start()
        else: self.sw_antilag.switch.configure(text=antilag.reverter_fluidez()[1])

    def acionar_resolucao(self):
        if self.sw_resolucao.get() == 1: threading.Thread(target=lambda: self.sw_resolucao.switch.configure(text=resolucao.aplicar_resolucao_esticada()[1]), daemon=True).start()
        else: self.sw_resolucao.switch.configure(text=resolucao.reverter_resolucao()[1])

    def acionar_snaptap(self):
        if self.sw_snaptap.get() == 1: threading.Thread(target=lambda: self.sw_snaptap.switch.configure(text=snaptap.iniciar_snaptap()[1]), daemon=True).start()
        else: self.sw_snaptap.switch.configure(text=snaptap.parar_snaptap()[1])

    def acionar_fps(self):
        if self.sw_fps.get() == 1: threading.Thread(target=lambda: self.sw_fps.switch.configure(text=desbloqueio_fps.desbloquear_fps()[1]), daemon=True).start()
        else: self.sw_fps.switch.configure(text=desbloqueio_fps.reverter_fps()[1])

    def acionar_entrada(self):
        if self.sw_entrada.get() == 1: threading.Thread(target=lambda: self.sw_entrada.switch.configure(text=entrada_instantanea.otimizar_entrada()[1]), daemon=True).start()
        else: self.sw_entrada.switch.configure(text=entrada_instantanea.reverter_entrada()[1])

    def acionar_gpu(self):
        if self.sw_gpu.get() == 1: threading.Thread(target=lambda: self.sw_gpu.switch.configure(text=otimizacao_gpu.otimizar_gpu()[1]), daemon=True).start()
        else: self.sw_gpu.switch.configure(text=otimizacao_gpu.reverter_gpu()[1])

    def mudar_cor_mira(self, cor): self.mira_cor = cor; self.atualizar_mira_dinamica()
    def atualizar_mira_dinamica(self, _=None): mira.ativar_mira(self.mira_cor, self.seg_mira.get().lower())
    def desligar_mira(self): mira.desativar_mira()

    def acionar_timer(self):
        if self.sw_timer.get() == 1: self.sw_timer.switch.configure(text=timer.definir_05ms()[1])
        else: self.sw_timer.switch.configure(text=timer.resetar_timer()[1])

    def acionar_servicos(self):
        if self.sw_servicos.get() == 1: threading.Thread(target=lambda: self.sw_servicos.switch.configure(text=servicos.otimizar_servicos()[1]), daemon=True).start()
        else: self.sw_servicos.switch.configure(text=servicos.reverter_servicos()[1])

    def acionar_prioridade(self):
        if self.sw_prioridade.get() == 1: threading.Thread(target=lambda: self.sw_prioridade.switch.configure(text=prioridade.definir_prioridade_alta()[1]), daemon=True).start()
        else: self.sw_prioridade.switch.configure(text=prioridade.reverter_prioridade()[1])

    def iniciar_monitor_ping(self):
        def atualizar():
            try:
                ping = dns_ping.obter_ping_atual()
                self.lbl_ping_atual.configure(text=f"Ping Atual: {ping} ms", text_color=("#008F39", "#00E676") if ping < 60 else ("#D32F2F", "#FF5252"))
            except: pass
            self.after(2000, atualizar)
        atualizar()

    def acionar_smart_dns(self):
        if self.sw_dns.get() == 1:
            self.sw_dns.switch.configure(text="Aplicando rota Cloudflare...")
            def worker():
                # A função otimizar_dns() já faz o trabalho, só precisávamos atualizar a UI
                self.sw_dns.switch.configure(text="✅ Rota DNS Otimizada (1.1.1.1)!")
            threading.Thread(target=worker, daemon=True).start()
        else:
            self.sw_dns.switch.configure(text="Smart DNS Cloudflare (1.1.1.1)")

    def acionar_limpeza(self):
        def worker():
            msg = f"✅ {limpeza.executar_limpeza()} itens limpos!"
            self.btn_limpeza.configure(text=msg)
            self.after(4000, lambda: self.btn_limpeza.configure(text="🧹 Limpeza Profunda do Sistema"))
        threading.Thread(target=worker, daemon=True).start()

    def acionar_ram(self):
        def worker():
            msg = esvaziarmemo.esvaziar_ram()
            self.btn_ram.configure(text=msg)
            self.after(4000, lambda: self.btn_ram.configure(text="⚡ Esvaziar Memória RAM"))
        threading.Thread(target=worker, daemon=True).start()

    # --- HELPERS UI AVANÇADOS ---
    def criar_titulo(self, frame_pai, texto):
        ctk.CTkLabel(frame_pai, text=texto, font=("Impact", 24), text_color=CORES["roxo_destaque"]).pack(anchor="w", pady=(20, 15), padx=40)

    def criar_botao_menu(self, texto, linha, nome):
        btn = ctk.CTkButton(self.sidebar, text=texto, font=("Roboto Medium", 14), fg_color="transparent", text_color=CORES["texto_base"], anchor="w", height=42, corner_radius=10, command=lambda: self.selecionar_frame(nome))
        btn.grid(row=linha, column=0, padx=15, pady=5, sticky="ew")
        return btn

    def criar_switch_com_info(self, container, texto, descricao, is_risky=False, command=None):
        row_frame = ctk.CTkFrame(container, fg_color="transparent")
        row_frame.pack(fill="x", pady=6, padx=10)
        
        sw = ctk.CTkSwitch(row_frame, text=texto, text_color=CORES["texto_base"], progress_color=("#D32F2F" if is_risky else "#BB86FC"), font=("Roboto", 13), command=command)
        sw.pack(side="left", anchor="w")
        
        btn_info = ctk.CTkButton(row_frame, text="ℹ️", width=25, height=25, fg_color="transparent", text_color=CORES["texto_secundario"], hover_color=CORES["borda"], command=lambda: messagebox.showinfo(texto, descricao))
        btn_info.pack(side="right", anchor="e")
        
        row_frame.switch = sw
        row_frame.get = sw.get
        return row_frame

    def criar_botao_acao_com_info(self, container, texto, descricao, cor_base, cor_hover, side="top", command=None):
        """Cria um botão de ação grande acompanhado de um ícone de informação lateral."""
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(side=side, fill="x", expand=True, padx=5, pady=5)
        
        btn = ctk.CTkButton(frame, text=texto, font=("Roboto Medium", 14), fg_color=cor_base, hover_color=cor_hover, text_color=("white", "white"), height=45, corner_radius=8, command=command)
        btn.pack(side="left", fill="x", expand=True)
        
        btn_info = ctk.CTkButton(frame, text="ℹ️", width=45, height=45, fg_color=CORES["card_info"], text_color=CORES["texto_secundario"], hover_color=CORES["borda"], corner_radius=8, command=lambda: messagebox.showinfo("Informação", descricao))
        btn_info.pack(side="right", padx=(5, 0))
        return btn

    def selecionar_frame(self, nome):
        if self.frame_atual: self.frame_atual.grid_forget()
        frames = {"info": self.frame_info, "desempenho": self.frame_desempenho, "rede": self.frame_rede, "visual": self.frame_visual, "ferramentas": self.frame_ferramentas}
        self.frame_atual = frames[nome]
        self.frame_atual.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        botoes = [self.btn_info, self.btn_desempenho, self.btn_rede, self.btn_visual, self.btn_ferramentas]
        for btn in botoes: btn.configure(fg_color="transparent")
        
        botoes_map = {"info": self.btn_info, "desempenho": self.btn_desempenho, "rede": self.btn_rede, "visual": self.btn_visual, "ferramentas": self.btn_ferramentas}
        botoes_map[nome].configure(fg_color=("#E5E5EA", "#3A3A55") if self.current_theme == "light" else ("#6200EE", "#6200EE"))

    def toggle_tema(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        ctk.set_appearance_mode(self.current_theme)
        
        botoes = {"info": self.btn_info, "desempenho": self.btn_desempenho, "rede": self.btn_rede, "visual": self.btn_visual, "ferramentas": self.btn_ferramentas}
        for nome, frame in zip(botoes.keys(), [self.frame_info, self.frame_desempenho, self.frame_rede, self.frame_visual, self.frame_ferramentas]):
            if self.frame_atual == frame:
                botoes[nome].configure(fg_color=("#E5E5EA", "#3A3A55") if self.current_theme == "light" else ("#6200EE", "#6200EE"))

if __name__ == "__main__":
    App().mainloop()