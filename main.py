import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import threading
import queue
import time
import psutil
import platform
import subprocess
import ctypes

# Módulos de otimização
import limpeza, esvaziarmemo, dns_ping, prioridade, mira, servicos, timer
import otimizacao_gpu, entrada_instantanea, antilag
import resolucao, snaptap, tcp_otimizar, ping_overlay, tela_cheia, unpark_cpu
import mira_bruta, shaders, potato_mode, game_booster, carregamento_turbo
import limpeza_bloodstrike, telemetria_win, input_lag_remover

# Módulos novos / corrigidos
import overlay_pro        # tracker de hardware
import stats_hud          # overlay Kill / HS / K/D com cronômetro
import fps_turbo_bs       # otimização avançada de FPS para Blood Strike
import modo_competitivo_bs  # desativa animações nos .ini do BS
import bs_server_ping     # pinga servidores NetEase do BS
import audio_competitivo  # realça passos e melhora áudio direcional
import fov_helper         # ajuste de FOV no .ini do BS
import bs_config_backup   # backup e restauro de configs do BS

# ==============================================================================
# DESIGN SYSTEM
# ==============================================================================
ctk.set_appearance_mode("dark")

CORES = {
    "bg_principal":    "#050508",
    "bg_sidebar":      "#08080C",
    "texto_base":      "#F8FAFC",
    "texto_secundario":"#94A3B8",
    "roxo_destaque":   "#8B5CF6",
    "roxo_hover":      "#A855F7",
    "verde_neon":      "#00E676",
    "vermelho_neon":   "#FF3A3A",
    "card_info":       "#12121A",
    "borda":           "#1E1E2E",
    "azul_neon":       "#00E5FF",
    "laranja":         "#FF6D00",
}


class App(ctk.CTk):
    def __init__(self, username="Visitante", dias_restantes=0):
        super().__init__()

        self.username       = username
        self.dias_restantes = dias_restantes

        self.title("Blood Strike Optimizer Pro v3.0 | Premium Edition")
        self.geometry("1050x720")
        self.resizable(False, False)
        self.configure(fg_color=CORES["bg_principal"])

        self.frame_atual = None
        self.mira_cor    = "#00E676"
        
        self.fila_ui = queue.Queue()
        self._processar_fila_ui()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ==============================================================
        # BARRA LATERAL (SIDEBAR)
        # ==============================================================
        self.sidebar = ctk.CTkFrame(
            self, width=260, corner_radius=0,
            fg_color=CORES["bg_sidebar"],
            border_width=1, border_color=CORES["borda"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        # Logo Premium na Sidebar
        try:
            raw_img = Image.open("logo.png")
            self.logo_img = ctk.CTkImage(light_image=raw_img, dark_image=raw_img, size=(110, 110))
            self.lbl_logo = ctk.CTkLabel(self.sidebar, image=self.logo_img, text="")
            self.lbl_logo.grid(row=1, column=0, padx=20, pady=(35, 10))
        except Exception:
            ctk.CTkLabel(
                self.sidebar, text="⚡ BS OPTIMIZER",
                font=ctk.CTkFont(size=24, weight="bold", family="Orbitron"),
                text_color=CORES["roxo_destaque"]
            ).grid(row=1, column=0, padx=20, pady=(40, 20))

        self.lbl_versao = ctk.CTkLabel(self.sidebar, text="ELITE EDITION v3.5", font=("Inter", 11, "bold"), text_color="#444466")
        self.lbl_versao.grid(row=2, column=0, pady=(0, 25))

        # Botões de menu
        self.btn_info        = self.criar_botao_menu("📊 Hardware Info",        2, "info")
        self.btn_desempenho  = self.criar_botao_menu("🚀 Desempenho Max",       3, "desempenho")
        self.btn_rede        = self.criar_botao_menu("🌐 Conexão e Ping",       4, "rede")
        self.btn_visual      = self.criar_botao_menu("🎯 Interface e Tracker",  5, "visual")
        self.btn_ferramentas = self.criar_botao_menu("🛠️ Ferramentas Pro",      6, "ferramentas")
        self.btn_stats       = self.criar_botao_menu("🎮 Blood Strike Stats",   7, "stats")

        # Painel de licença e Suporte
        sessao = ctk.CTkFrame(self.sidebar, fg_color=CORES["card_info"], corner_radius=15, border_width=1, border_color=CORES["borda"])
        sessao.grid(row=10, column=0, sticky="s", pady=20, padx=15)
        
        ctk.CTkLabel(sessao, text=f"👤 {self.username}",
                     font=("Inter", 14, "bold"), text_color=CORES["texto_base"]).pack(pady=(12, 0))
        
        vip_tag = ctk.CTkFrame(sessao, fg_color="#0a1a12", corner_radius=20, border_width=1, border_color="#00e676")
        vip_tag.pack(pady=5, padx=15)
        ctk.CTkLabel(vip_tag, text=f"👑 VIP: {self.dias_restantes} DIAS",
                     font=("Inter", 11, "bold"), text_color=CORES["verde_neon"]).pack(padx=12, pady=4)

        # Botão Suporte WhatsApp
        self.btn_suporte = ctk.CTkButton(
            sessao, text="💬 SUPORTE WHATSAPP", 
            font=("Inter", 11, "bold"), height=32,
            fg_color="#25D366", hover_color="#128C7E",
            text_color="#fff", corner_radius=8,
            command=self.abrir_suporte_whatsapp
        )
        self.btn_suporte.pack(pady=(5, 12), padx=15)

        # Helper de layout
        def cfg(frame):
            frame.grid_columnconfigure(0, weight=1)
            return frame

        # ==============================================================
        # 0. HARDWARE INFO
        # ==============================================================
        self.frame_info = cfg(ctk.CTkFrame(self, fg_color="transparent"))
        self.criar_titulo(self.frame_info, "DIAGNÓSTICO DO SISTEMA")
        self.criar_painel_hardware(self.frame_info)

        # ==============================================================
        # 1. DESEMPENHO
        # ==============================================================
        self.frame_desempenho = cfg(ctk.CTkFrame(self, fg_color="transparent"))
        self.criar_titulo(self.frame_desempenho, "OTIMIZAÇÃO DE DESEMPENHO")

        sw_container = ctk.CTkFrame(self.frame_desempenho, fg_color="transparent")
        sw_container.pack(fill="x", padx=30, pady=5)

        col_esq = ctk.CTkFrame(sw_container, fg_color="transparent")
        col_esq.pack(side="left", fill="both", expand=True)
        col_dir = ctk.CTkFrame(sw_container, fg_color="transparent")
        col_dir.pack(side="right", fill="both", expand=True)

        # col_esq — otimizações de CPU / sistema
        self.sw_fps_turbo    = self.criar_switch_com_info(col_esq, "⚡ FPS Turbo Blood Strike",      "Remove VSync, GameDVR e configura GPU Priority máxima. Inclui desbloqueio total de FPS nos .ini do BS.", command=self.acionar_fps_turbo)
        self.sw_antilag      = self.criar_switch_com_info(col_esq, "Modo Antilag (Zero Delay)",     "Desativa o GameDVR e otimizações de tela cheia.",                   command=self.acionar_antilag)
        self.sw_timer        = self.criar_switch_com_info(col_esq, "Sincronização Precisão (0.5ms)","Ajusta o relógio interno do Windows para 0.5ms.",                   command=self.acionar_timer)
        self.sw_prioridade   = self.criar_switch_com_info(col_esq, "Foco Extremo Processador",      "Força o Windows a dar prioridade máxima ao jogo.",                  command=self.acionar_prioridade)
        self.sw_competitivo  = self.criar_switch_com_info(col_esq, "🎯 Modo Competitivo BS",         "Desativa sombras, blur e animações desnecessárias no .ini do BS.",  command=self.acionar_modo_competitivo)

        # col_dir — otimizações de GPU / hardware
        self.sw_gpu          = self.criar_switch_com_info(col_dir, "Overdrive de Placa de Vídeo",    "Ativa o plano de 'Alto Desempenho' da GPU.",                        command=self.acionar_gpu)
        self.sw_potato       = self.criar_switch_com_info(col_dir, "Modo Ultra-Leve (Potato)",       "Desativa sombras e texturas na raiz do jogo.",                      command=self.acionar_potato)
        self.sw_carregamento = self.criar_switch_com_info(col_dir, "Carregamento Turbo de Mapas",    "Usa RAM+SysMain OFF para mapas carregarem em segundos.",             command=self.acionar_carregamento)
        self.sw_mira_bruta   = self.criar_switch_com_info(col_dir, "Precisão Bruta do Mouse (1:1)", "Desliga a aceleração nativa do Windows.",                            command=self.acionar_mira_bruta)
        self.sw_input_lag    = self.criar_switch_com_info(col_dir, "Delay 0 Teclado/Mouse (MMCSS)", "Ajusta o Win32Priority do sistema.",                                 command=self.acionar_input_lag)

        # Botões de ação
        botoes1 = ctk.CTkFrame(self.frame_desempenho, fg_color="transparent")
        botoes1.pack(fill="x", padx=35, pady=(10, 0))
        self.btn_limpeza  = self.criar_botao_acao_com_info(botoes1, "🧹 Limpeza do Sistema",       "Limpa cache e temporários do Windows.",           CORES["roxo_destaque"], CORES["roxo_hover"], side="left",  command=self.acionar_limpeza)
        self.btn_shaders  = self.criar_botao_acao_com_info(botoes1, "🔧 Recriar Shaders",          "Exclui cache antigo da placa de vídeo.",          "#d35400", "#e67e22",               side="right", command=self.acionar_shaders)

        botoes2 = ctk.CTkFrame(self.frame_desempenho, fg_color="transparent")
        botoes2.pack(fill="x", padx=35, pady=(10, 0))
        self.btn_limpeza_bs = self.criar_botao_acao_com_info(botoes2, "🗑️ Wipe Cache Blood Strike", "Limpa erros e logs antigos para evitar crashes.", CORES["vermelho_neon"], "#d32f2f",  side="left",  command=self.acionar_limpeza_bs)

        # ==============================================================
        # 2. REDE
        # ==============================================================
        self.frame_rede = cfg(ctk.CTkFrame(self, fg_color="transparent"))
        self.criar_titulo(self.frame_rede, "REDE E LATÊNCIA")

        self.ping_frame = ctk.CTkFrame(
            self.frame_rede, fg_color=CORES["card_info"],
            corner_radius=15, border_width=1, border_color=CORES["borda"]
        )
        self.ping_frame.pack(fill="x", padx=40, pady=(0, 20))
        self.lbl_ping_atual = ctk.CTkLabel(
            self.ping_frame, text="Ping Atual: -- ms",
            font=("Inter", 24, "bold"), text_color=CORES["texto_base"]
        )
        self.lbl_ping_atual.pack(pady=25)

        container_rede = ctk.CTkFrame(self.frame_rede, fg_color="transparent")
        container_rede.pack(fill="x", padx=40)
        self.sw_dns         = self.criar_switch_com_info(container_rede, "Smart DNS Cloudflare (1.1.1.1)", "Altera a sua rota de internet para a Cloudflare.",              command=self.acionar_smart_dns)
        self.sw_tcp         = self.criar_switch_com_info(container_rede, "Otimizar Roteamento TCP/IP",     "Limpa o cache de rede e reseta a placa.",                       command=self.acionar_tcp)
        self.sw_low_lat     = self.criar_switch_com_info(container_rede, "🔥 Modo Baixa Latência Win",  "Define NetworkThrottlingIndex máximo (0xFFFFFFFF) no registro.",  command=self.acionar_low_latency)
        self.sw_ping_overlay= self.criar_switch_com_info(container_rede, "Ping HUD Externo",               "Abre um contador de Ping por cima do jogo.",                    command=self.acionar_ping_overlay)

        # Painel de servidores BS
        srv_card = ctk.CTkFrame(
            self.frame_rede, fg_color=CORES["card_info"],
            corner_radius=12, border_width=1, border_color=CORES["borda"]
        )
        srv_card.pack(fill="x", padx=40, pady=(15, 5))
        ctk.CTkLabel(
            srv_card, text="📡  Servidores Blood Strike — Menor Latência",
            font=("Inter", 13, "bold"), text_color=CORES["roxo_destaque"]
        ).pack(pady=(12, 5))
        self.lbl_servidores = ctk.CTkLabel(
            srv_card, text="Clique em Medir para testar os servidores NetEase.",
            font=("Inter", 11), text_color=CORES["texto_secundario"],
            wraplength=450, justify="left"
        )
        self.lbl_servidores.pack(padx=15, pady=(0, 5))
        self.btn_medir_srv = ctk.CTkButton(
            srv_card, text="📶 Medir Servidores",
            font=("Inter", 13, "bold"), height=36,
            fg_color=CORES["azul_neon"], hover_color="#005f73",
            text_color="#000", corner_radius=8,
            command=self.acionar_medir_servidores
        )
        self.btn_medir_srv.pack(padx=15, pady=(5, 12))

        # ==============================================================
        # 3. INTERFACE & TRACKER
        # ==============================================================
        self.frame_visual = cfg(ctk.CTkFrame(self, fg_color="transparent"))
        self.criar_titulo(self.frame_visual, "MIRA E INTERFACE")

        self.seg_mira = ctk.CTkSegmentedButton(
            self.frame_visual, values=["Padrão", "Ponto", "Pequeno"],
            selected_color=CORES["roxo_destaque"],
            selected_hover_color=CORES["roxo_hover"],
            command=self.atualizar_mira_dinamica
        )
        self.seg_mira.set("Padrão")
        self.seg_mira.pack(pady=10, padx=40, fill="x")

        mira_frame = ctk.CTkFrame(self.frame_visual, fg_color="transparent")
        mira_frame.pack(padx=40, pady=10)
        for cor in ["#FF1744", "#00E676", "#00E5FF", "#D500F9"]:
            ctk.CTkButton(
                mira_frame, text="✛", width=50, height=50,
                text_color=cor, font=("Arial", 20, "bold"),
                fg_color=CORES["card_info"], hover_color=CORES["borda"],
                command=lambda c=cor: self.mudar_cor_mira(c)
            ).pack(side="left", padx=5)
        ctk.CTkButton(
            mira_frame, text="OFF", width=50, height=50,
            text_color="#fff", fg_color=CORES["vermelho_neon"],
            hover_color="#d32f2f", command=self.desligar_mira
        ).pack(side="left", padx=5)

        container_vis = ctk.CTkFrame(self.frame_visual, fg_color="transparent")
        container_vis.pack(fill="x", padx=40, pady=20)
        self.sw_tela_cheia = self.criar_switch_com_info(container_vis, "Forçar Tela Cheia Exclusiva", "Ignora o Borderless e força tela cheia real.",       command=self.acionar_tela_cheia)
        self.sw_resolucao  = self.criar_switch_com_info(container_vis, "Forçar Resolução Esticada",   "Alarga os modelos dos inimigos.",                     command=self.acionar_resolucao)
        self.sw_tracker    = self.criar_switch_com_info(container_vis, "Monitor Hardware (Tracker)",  "Exibe uso de CPU e RAM transparentes por cima do jogo.", command=self.acionar_tracker)

        # ==============================================================
        # 4. FERRAMENTAS PRO
        # ==============================================================
        self.frame_ferramentas = cfg(ctk.CTkFrame(self, fg_color="transparent"))
        self.criar_titulo(self.frame_ferramentas, "FERRAMENTAS PRO")

        container_pro = ctk.CTkFrame(self.frame_ferramentas, fg_color="transparent")
        container_pro.pack(fill="x", padx=40)
        self.sw_snaptap   = self.criar_switch_com_info(container_pro, "Teclado SnapTap (Software)",     "Anula o atraso de Strafe A+D.",                              is_risky=True, command=self.acionar_snaptap)
        self.sw_unpark    = self.criar_switch_com_info(container_pro, "Unpark CPU (Acordar Núcleos)",   "Impede o Windows de adormecer o processador.",                command=self.acionar_unpark)
        self.sw_servicos  = self.criar_switch_com_info(container_pro, "Suspender Bloatware Windows",    "Desativa processos inúteis enquanto joga.",                   command=self.acionar_servicos)
        self.sw_telemetria= self.criar_switch_com_info(container_pro, "Matar Telemetria MS",            "Bloqueia rastreamento em segundo plano.",                     command=self.acionar_telemetria)
        self.sw_entrada   = self.criar_switch_com_info(container_pro, "Skip Intro (Pular Abertura)",    "Oculta vídeos de inicialização do jogo.",                      command=self.acionar_entrada)
        self.sw_audio     = self.criar_switch_com_info(container_pro, "🔊 Áudio Competitivo (Passos)",   "Realça som de passos e melhora localização direcional.",         command=self.acionar_audio_competitivo)

        # Linha de FOV
        fov_row = ctk.CTkFrame(container_pro, fg_color="transparent")
        fov_row.pack(fill="x", pady=6, padx=10)
        ctk.CTkLabel(fov_row, text="📄 FOV do Blood Strike:",
                     font=("Inter", 13, "bold"), text_color=CORES["texto_base"]
                     ).pack(side="left", padx=(0, 10))
        self.seg_fov = ctk.CTkSegmentedButton(
            fov_row,
            values=list(fov_helper.FOV_PRESETS.keys()),
            selected_color=CORES["roxo_destaque"],
            selected_hover_color=CORES["roxo_hover"],
            command=self.acionar_fov
        )
        self.seg_fov.set("Padrão (70°)")
        self.seg_fov.pack(side="left", fill="x", expand=True)

        botoes_ferr = ctk.CTkFrame(self.frame_ferramentas, fg_color="transparent")
        botoes_ferr.pack(fill="x", padx=35, pady=(15, 0))
        self.btn_booster  = self.criar_botao_acao_com_info(botoes_ferr, "🚀 Game Booster Extremo",  "Mata processos pesados secundários.",           CORES["vermelho_neon"], "#d32f2f", side="top", command=self.acionar_booster)
        self.btn_ram      = self.criar_botao_acao_com_info(botoes_ferr, "⚡ Esvaziar Memória RAM",  "Libera a memória RAM em espera.",               CORES["verde_neon"],    "#00c853", side="top", command=self.acionar_ram)
        self.btn_ram.configure(text_color="#000")
        self.btn_backup   = self.criar_botao_acao_com_info(botoes_ferr, "💾 Backup Config BS",      "Salva todos os .ini do BS em arquivo .zip.",    "#0077b6", "#023e8a",         side="top", command=self.acionar_backup_config)
        self.btn_restaurar= self.criar_botao_acao_com_info(botoes_ferr, "📂 Restaurar Último Backup", "Restaura os .ini do último backup disponível.", "#4a4e69", "#22223b",         side="top", command=self.acionar_restaurar_backup)

        # ==============================================================
        # 5. BLOOD STRIKE STATS  ← NOVO MENU
        # ==============================================================
        self.frame_stats = cfg(ctk.CTkFrame(self, fg_color="transparent"))
        self.criar_titulo(self.frame_stats, "BLOOD STRIKE STATS")
        self._criar_painel_stats()

        # Inicialização
        self.selecionar_frame("info")
        self.iniciar_monitor_ping()

    def _processar_fila_ui(self):
        try:
            while True:
                self.fila_ui.get_nowait()()
        except queue.Empty:
            pass
        finally:
            self.after(20, self._processar_fila_ui)

    def ui_segura(self, func):
        """Executa uma função na thread principal de forma segura."""
        self.fila_ui.put(func)

    def _criar_painel_stats(self):
        """Monta o painel de estatísticas de partida com cronômetro e histórico."""

        # ── Card principal de stats ───────────────────────────────────────────
        card = ctk.CTkFrame(
            self.frame_stats, fg_color=CORES["card_info"],
            corner_radius=15, border_width=1, border_color=CORES["borda"]
        )
        card.pack(fill="x", padx=40, pady=(0, 10))

        # Header com título e cronômetro
        hdr = ctk.CTkFrame(card, fg_color="#1a0a2e", corner_radius=10)
        hdr.pack(fill="x", padx=12, pady=(12, 5))
        ctk.CTkLabel(
            hdr, text="📊  Estatísticas da Partida",
            font=("Inter", 14, "bold"), text_color=CORES["roxo_destaque"]
        ).pack(side="left", padx=12, pady=8)
        self.lbl_s_timer = ctk.CTkLabel(
            hdr, text="⏱ 00:00",
            font=("Inter", 14, "bold"), text_color=CORES["azul_neon"]
        )
        self.lbl_s_timer.pack(side="right", padx=12, pady=8)
        self._tick_painel_timer()

        # Grid de 3 colunas
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=5)
        for i in range(3):
            grid.grid_columnconfigure(i, weight=1)

        def _stat_card(pai, titulo, cor, col):
            f = ctk.CTkFrame(pai, fg_color="#1a1a28", corner_radius=10)
            f.grid(row=0, column=col, padx=8, pady=5, sticky="ew")
            ctk.CTkLabel(f, text=titulo, font=("Inter", 12, "bold"), text_color=cor).pack(pady=(10, 2))
            lbl = ctk.CTkLabel(f, text="0", font=("Impact", 36), text_color=cor)
            lbl.pack(pady=(0, 10))
            return lbl

        self.lbl_s_kills  = _stat_card(grid, "🎯 KILLS",     CORES["verde_neon"],    0)
        self.lbl_s_hs     = _stat_card(grid, "💥 HEADSHOTS", CORES["roxo_destaque"], 1)
        self.lbl_s_mortes = _stat_card(grid, "⚔️ MORTES",    CORES["vermelho_neon"], 2)

        # K/D e HS%
        kd_frame = ctk.CTkFrame(card, fg_color="transparent")
        kd_frame.pack(fill="x", padx=20, pady=(5, 5))
        kd_frame.grid_columnconfigure(0, weight=1)
        kd_frame.grid_columnconfigure(1, weight=1)

        def _ratio_card(pai, titulo, cor, col):
            f = ctk.CTkFrame(pai, fg_color="#1a1a28", corner_radius=10)
            f.grid(row=0, column=col, padx=8, pady=5, sticky="ew")
            ctk.CTkLabel(f, text=titulo, font=("Inter", 11, "bold"), text_color=cor).pack(pady=(8, 2))
            lbl = ctk.CTkLabel(f, text="0.0", font=("Impact", 28), text_color=cor)
            lbl.pack(pady=(0, 8))
            return lbl

        self.lbl_s_kd    = _ratio_card(kd_frame, "⚔️  K/D Ratio", CORES["azul_neon"], 0)
        self.lbl_s_hspct = _ratio_card(kd_frame, "🎯  HS%",        CORES["laranja"],  1)

        # Botões +Kill / +HS / +Morte
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(5, 5))

        def _mini_btn(pai, texto, cor, cmd):
            ctk.CTkButton(
                pai, text=texto, font=("Inter", 12, "bold"),
                fg_color=CORES["borda"], hover_color=cor,
                text_color=cor, height=36, corner_radius=8, command=cmd
            ).pack(side="left", expand=True, fill="x", padx=4)

        _mini_btn(btn_row, "+Kill  [F5]",  CORES["verde_neon"],    lambda: self._incrementar_stat("kills"))
        _mini_btn(btn_row, "+HS    [F6]",  CORES["roxo_destaque"], lambda: self._incrementar_stat("hs"))
        _mini_btn(btn_row, "+Morte [F7]",  CORES["vermelho_neon"], lambda: self._incrementar_stat("mortes"))

        btn_reset_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_reset_row.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkButton(
            btn_reset_row, text="↺  Nova Partida (Reset + Salva no Histórico)",
            font=("Inter", 12, "bold"), fg_color="#1e1e2e",
            hover_color=CORES["borda"], text_color=CORES["texto_secundario"],
            height=36, corner_radius=8, command=self._resetar_stats
        ).pack(fill="x", padx=4)

        # Info de atalhos
        ctk.CTkLabel(
            self.frame_stats,
            text="⌨️  F5 = +Kill  |  F6 = +HS  |  F7 = +Morte  |  F8 = Nova Partida",
            font=("Inter", 11), text_color=CORES["texto_secundario"]
        ).pack(pady=(2, 5))

        # ── Card de histórico ─────────────────────────────────────────────────
        hist_card = ctk.CTkFrame(
            self.frame_stats, fg_color=CORES["card_info"],
            corner_radius=12, border_width=1, border_color=CORES["borda"]
        )
        hist_card.pack(fill="x", padx=40, pady=(5, 5))
        ctk.CTkLabel(
            hist_card, text="📜  Últimas Partidas",
            font=("Inter", 13, "bold"), text_color=CORES["roxo_destaque"]
        ).pack(anchor="w", padx=15, pady=(10, 3))
        self.lbl_historico = ctk.CTkLabel(
            hist_card, text="Nenhuma partida registrada ainda.",
            font=("Inter", 11), text_color=CORES["texto_secundario"],
            anchor="w", justify="left"
        )
        self.lbl_historico.pack(anchor="w", padx=15, pady=(0, 5))
        self._atualizar_historico_label()
        ctk.CTkButton(
            hist_card, text="📈 Exportar CSV",
            font=("Inter", 11, "bold"), height=30,
            fg_color="#1e1e2e", hover_color="#2a2a3e",
            text_color=CORES["verde_neon"], corner_radius=8,
            command=self._exportar_csv
        ).pack(anchor="e", padx=15, pady=(0, 10))

        # Switch HUD overlay
        container_s = ctk.CTkFrame(self.frame_stats, fg_color="transparent")
        container_s.pack(fill="x", padx=40, pady=5)
        self.sw_stats_hud = self.criar_switch_com_info(
            container_s, "Stats HUD (Overlay in-game)",
            "Exibe Kill/HS/K/D por cima do jogo. Cronometrado automaticamente. Use F5-F8.",
            command=self.acionar_stats_hud
        )

    def _tick_painel_timer(self):
        """Atualiza o cronômetro do painel interno a cada segundo."""
        try:
            self.lbl_s_timer.configure(text=f"⏱ {stats_hud.obter_tempo_sessao()}")
        except Exception:
            pass
        self.after(1000, self._tick_painel_timer)

    def _atualizar_historico_label(self):
        """Carrega e exibe as últimas 5 partidas no painel."""
        try:
            historico = stats_hud.obter_historico()[-5:]
            if not historico:
                self.lbl_historico.configure(text="Nenhuma partida registrada ainda.")
                return
            linhas = []
            for i, p in enumerate(reversed(historico), 1):
                linhas.append(
                    f"#{i} | {p['data']} | {p['duracao']} | "
                    f"K:{p['kills']} HS:{p['hs']} D:{p['mortes']} | "
                    f"K/D:{p['kd']} HS%:{p['hs_pct']}"
                )
            self.lbl_historico.configure(text="\n".join(linhas))
        except Exception:
            pass

    def _exportar_csv(self):
        caminho = stats_hud.exportar_historico_csv()
        if caminho:
            messagebox.showinfo("✅ CSV Exportado", f"Arquivo salvo em:\n{caminho}")
        else:
            messagebox.showwarning("Sem dados", "Nenhuma partida registrada para exportar.")

    # ── Lógica dos stats (painel interno + sync com HUD overlay) ──────────────
    def _incrementar_stat(self, chave):
        import stats_hud as sh
        sh._stats[chave] += 1
        if sh._hud_app and sh._hud_app.winfo_exists():
            sh._hud_app.after(0, sh._hud_app._atualizar_labels)
        self._sincronizar_labels_stats()
        self._atualizar_historico_label()

    def _resetar_stats(self):
        import stats_hud as sh
        # Delega para o HUD (que salva no histórico)
        if sh._hud_app and sh._hud_app.winfo_exists():
            sh._hud_app.after(0, sh._hud_app._reset)
        else:
            sh._stats["kills"] = 0
            sh._stats["hs"]    = 0
            sh._stats["mortes"]= 0
        self._sincronizar_labels_stats()
        self.after(500, self._atualizar_historico_label)

    def _sincronizar_labels_stats(self):
        """Atualiza os labels do painel interno com os valores atuais."""
        import stats_hud as sh
        k  = sh._stats["kills"]
        hs = sh._stats["hs"]
        m  = sh._stats["mortes"]
        kd_val = f"{k / m:.2f}" if m > 0 else (f"{k}.0" if k > 0 else "0.0")
        hs_val = f"{hs / k * 100:.0f}%" if k > 0 else "0%"
        self.lbl_s_kills.configure(text=str(k))
        self.lbl_s_hs.configure(text=str(hs))
        self.lbl_s_mortes.configure(text=str(m))
        self.lbl_s_kd.configure(text=kd_val)
        self.lbl_s_hspct.configure(text=hs_val)

    # ==================================================================
    # LÓGICA VISUAL DOS SWITCHES
    # ==================================================================
    def atualizar_ui_switch(self, sw_obj, ativado, nome_base):
        if ativado:
            sw_obj.switch.configure(text=f"🟢 [ON] {nome_base}",  text_color=CORES["verde_neon"])
        else:
            sw_obj.switch.configure(text=f"⚪ [OFF] {nome_base}", text_color=CORES["texto_secundario"])

    # ==================================================================
    # HARDWARE INFO
    # ==================================================================
    def criar_painel_hardware(self, frame_pai):
        panel = ctk.CTkFrame(
            frame_pai, fg_color=CORES["card_info"],
            corner_radius=15, border_width=1, border_color=CORES["borda"]
        )
        panel.pack(fill="x", padx=40, pady=(10, 20))
        ctk.CTkLabel(
            panel, text="Especificações Lidas do seu Computador:",
            font=("Inter", 14, "bold"), text_color=CORES["roxo_destaque"]
        ).pack(pady=(15, 5))

        info_frame = ctk.CTkFrame(panel, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)
        for i in range(2):
            info_frame.grid_columnconfigure(i, weight=1)

        info = self.obter_info_sistema()
        labels = [
            (f"🖥️ Processador: {info['cpu']}",      0, 0),
            (f"🎮 Placa de Vídeo: {info['gpu']}",    0, 1),
            (f"📟 Memória RAM: {info['ram']}",        1, 0),
            (f"💽 Armazenamento: {info['disk']}",     1, 1),
            (f"🕒 Taxa de Atualização: {info['refresh']}Hz", 2, 0),
            (f"⚙️ Sistema: {info['os']}",             2, 1),
        ]
        for text, r, c in labels:
            ctk.CTkLabel(
                info_frame, text=text,
                font=("Inter", 13), text_color=CORES["texto_base"], anchor="w"
            ).grid(row=r, column=c, padx=10, pady=8, sticky="w")

    def obter_info_sistema(self):
        try:
            sistema = f"{platform.system()} {platform.release()}"
            cpu = platform.processor()
            if "Windows" in platform.system():
                cpu = subprocess.check_output("wmic cpu get name", shell=True).decode().split('\n')[1].strip()
            gpu = "Integrada / Desconhecida"
            if "Windows" in platform.system():
                gpu_raw = subprocess.check_output("wmic path win32_VideoController get name", shell=True).decode().split('\n')
                gpu = gpu_raw[1].strip() if len(gpu_raw) > 1 else gpu
            ram   = f"{round(psutil.virtual_memory().total / (1024**3))} GB Instalados"
            usage = psutil.disk_usage('C:\\' if "Windows" in platform.system() else '/')
            disk  = f"{round(usage.total / (1024**3))} GB Total"
            refresh = 60
            if "Windows" in platform.system():
                u32 = ctypes.windll.user32
                refresh = u32.GetDeviceCaps(u32.GetDC(0), 116)
            return {"cpu": cpu[:35], "gpu": gpu[:30], "ram": ram, "disk": disk, "refresh": refresh, "os": sistema}
        except Exception:
            return {"cpu": "Aguardando...", "gpu": "Aguardando...", "ram": "--", "disk": "--", "refresh": "--", "os": "Desconhecido"}

    # ==================================================================
    # AÇÕES — DESEMPENHO
    # ==================================================================

    def acionar_modo_competitivo(self):
        ativado = self.sw_competitivo.get() == 1
        if ativado:
            threading.Thread(target=modo_competitivo_bs.aplicar_modo_competitivo, daemon=True).start()
        else:
            threading.Thread(target=modo_competitivo_bs.reverter_modo_competitivo, daemon=True).start()
        self.atualizar_ui_switch(self.sw_competitivo, ativado, "🎯 Modo Competitivo BS")

    def acionar_fps_turbo(self):
        """FPS Turbo avançado — novo módulo fps_turbo_bs."""
        ativado = self.sw_fps_turbo.get() == 1
        if ativado:
            threading.Thread(target=fps_turbo_bs.aplicar_fps_turbo, daemon=True).start()
        else:
            threading.Thread(target=fps_turbo_bs.reverter_fps_turbo, daemon=True).start()
        self.atualizar_ui_switch(self.sw_fps_turbo, ativado, "⚡ FPS Turbo Blood Strike")

    def acionar_antilag(self):
        ativado = self.sw_antilag.get() == 1
        if ativado:
            threading.Thread(target=antilag.otimizar_fluidez, daemon=True).start()
        else:
            antilag.reverter_fluidez()
        self.atualizar_ui_switch(self.sw_antilag, ativado, "Modo Antilag (Zero Delay)")

    def acionar_timer(self):
        ativado = self.sw_timer.get() == 1
        if ativado:
            timer.definir_05ms()
        else:
            timer.resetar_timer()
        self.atualizar_ui_switch(self.sw_timer, ativado, "Sincronização Precisão (0.5ms)")

    def acionar_prioridade(self):
        ativado = self.sw_prioridade.get() == 1
        if ativado:
            threading.Thread(target=prioridade.definir_prioridade_alta, daemon=True).start()
        else:
            prioridade.reverter_prioridade()
        self.atualizar_ui_switch(self.sw_prioridade, ativado, "Foco Extremo Processador")

    def acionar_telemetria(self):
        ativado = self.sw_telemetria.get() == 1
        if ativado:
            threading.Thread(target=telemetria_win.desativar_telemetria, daemon=True).start()
        else:
            telemetria_win.reverter_telemetria()
        self.atualizar_ui_switch(self.sw_telemetria, ativado, "Matar Telemetria MS")

    def acionar_gpu(self):
        ativado = self.sw_gpu.get() == 1
        if ativado:
            threading.Thread(target=otimizacao_gpu.otimizar_gpu, daemon=True).start()
        else:
            otimizacao_gpu.reverter_gpu()
        self.atualizar_ui_switch(self.sw_gpu, ativado, "Overdrive de Placa de Vídeo")

    def acionar_potato(self):
        ativado = self.sw_potato.get() == 1
        if ativado:
            threading.Thread(target=potato_mode.aplicar_potato, daemon=True).start()
        else:
            potato_mode.reverter_potato()
        self.atualizar_ui_switch(self.sw_potato, ativado, "Modo Ultra-Leve (Potato)")

    def acionar_carregamento(self):
        ativado = self.sw_carregamento.get() == 1
        if ativado:
            threading.Thread(target=carregamento_turbo.otimizar_carregamento, daemon=True).start()
        else:
            threading.Thread(target=carregamento_turbo.reverter_carregamento, daemon=True).start()
        self.atualizar_ui_switch(self.sw_carregamento, ativado, "Carregamento Turbo de Mapas")

    def acionar_mira_bruta(self):
        ativado = self.sw_mira_bruta.get() == 1
        if ativado:
            threading.Thread(target=mira_bruta.otimizar_mouse, daemon=True).start()
        else:
            mira_bruta.reverter_mouse()
        self.atualizar_ui_switch(self.sw_mira_bruta, ativado, "Precisão Bruta do Mouse (1:1)")

    def acionar_input_lag(self):
        ativado = self.sw_input_lag.get() == 1
        if ativado:
            threading.Thread(target=input_lag_remover.ajustar_mmcss_mouse, daemon=True).start()
        else:
            input_lag_remover.reverter_mmcss()
        self.atualizar_ui_switch(self.sw_input_lag, ativado, "Delay 0 Teclado/Mouse (MMCSS)")

    # Botões de ação — agora conectados aos módulos reais
    def acionar_limpeza(self):
        def worker():
            resultado = limpeza.executar_limpeza()
            msg = f"✅ {resultado} itens limpos!" if isinstance(resultado, int) else f"✅ {resultado}"
            self.ui_segura(lambda: self.btn_limpeza.configure(text=msg))
            time.sleep(3)
            self.ui_segura(lambda: self.btn_limpeza.configure(text="🧹 Limpeza do Sistema"))
        threading.Thread(target=worker, daemon=True).start()

    def acionar_shaders(self):
        """Chama shaders.py de verdade."""
        def worker():
            resultado = shaders.limpar_shaders()
            self.ui_segura(lambda: self.btn_shaders.configure(text=f"✅ Shaders Limpos!"))
            time.sleep(3)
            self.ui_segura(lambda: self.btn_shaders.configure(text="🔧 Recriar Shaders"))
        threading.Thread(target=worker, daemon=True).start()

    def acionar_limpeza_bs(self):
        def worker():
            sucesso, msg = limpeza_bloodstrike.limpar_cache_bs()
            self.ui_segura(lambda: self.btn_limpeza_bs.configure(text="✅ Cache BS Limpo!"))
            time.sleep(3)
            self.ui_segura(lambda: self.btn_limpeza_bs.configure(text="🗑️ Wipe Cache Blood Strike"))
        threading.Thread(target=worker, daemon=True).start()

    def acionar_ram(self):
        """Chama esvaziarmemo.py de verdade."""
        def worker():
            resultado = esvaziarmemo.esvaziar_ram()
            self.ui_segura(lambda: self.btn_ram.configure(text="✅ RAM Esvaziada!"))
            time.sleep(3)
            self.ui_segura(lambda: self.btn_ram.configure(text="⚡ Esvaziar Memória RAM"))
        threading.Thread(target=worker, daemon=True).start()

    def acionar_booster(self):
        """Chama game_booster.py de verdade."""
        def worker():
            resultado = game_booster.ativar_booster()
            self.ui_segura(lambda: self.btn_booster.configure(text="✅ Processos Mortos!"))
            time.sleep(3)
            self.ui_segura(lambda: self.btn_booster.configure(text="🚀 Game Booster Extremo"))
        threading.Thread(target=worker, daemon=True).start()

    # ==================================================================
    # AÇÕES — REDE
    # ==================================================================

    def acionar_smart_dns(self):
        ativado = self.sw_dns.get() == 1
        if ativado:
            self.sw_dns.switch.configure(text="Aplicando rota...", text_color=CORES["roxo_destaque"])
            def worker():
                import dns_ping as dp
                if hasattr(dp, 'aplicar_dns'):
                    dp.aplicar_dns()
                self.ui_segura(lambda: self.sw_dns.switch.configure(text="🟢 [ON] Smart DNS Cloudflare (1.1.1.1)", text_color=CORES["verde_neon"]))
            threading.Thread(target=worker, daemon=True).start()
        else:
            self.atualizar_ui_switch(self.sw_dns, False, "Smart DNS Cloudflare (1.1.1.1)")

    def acionar_tcp(self):
        ativado = self.sw_tcp.get() == 1
        if ativado:
            threading.Thread(target=tcp_otimizar.otimizar_tcp, daemon=True).start()
        else:
            tcp_otimizar.reverter_tcp()
        self.atualizar_ui_switch(self.sw_tcp, ativado, "Otimizar Roteamento TCP/IP")

    def acionar_ping_overlay(self):
        ativado = self.sw_ping_overlay.get() == 1
        if ativado:
            threading.Thread(target=ping_overlay.ativar_ping, daemon=True).start()
        else:
            ping_overlay.desativar_ping()
        self.atualizar_ui_switch(self.sw_ping_overlay, ativado, "Ping HUD Externo")

    def acionar_low_latency(self):
        """Ativa/desativa o NetworkThrottlingIndex máximo do Windows."""
        ativado = self.sw_low_lat.get() == 1
        if ativado:
            def _ligar():
                import subprocess
                subprocess.run(
                    r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" '
                    r'/v "NetworkThrottlingIndex" /t REG_DWORD /d "4294967295" /f',
                    shell=True, capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            threading.Thread(target=_ligar, daemon=True).start()
        else:
            def _desligar():
                import subprocess
                subprocess.run(
                    r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" '
                    r'/v "NetworkThrottlingIndex" /t REG_DWORD /d "10" /f',
                    shell=True, capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            threading.Thread(target=_desligar, daemon=True).start()
        self.atualizar_ui_switch(self.sw_low_lat, ativado, "🔥 Modo Baixa Latência Win")

    def acionar_medir_servidores(self):
        """Pinga os servidores BS em background e atualiza o label."""
        self.btn_medir_srv.configure(text="⏳ Medindo...", state="disabled")
        self.lbl_servidores.configure(text="Medindo latência dos servidores NetEase... aguarde.")

        def _worker():
            def _atualizar_parcial(parcial):
                linhas = []
                for nome, ping in sorted(parcial.items(), key=lambda x: x[1]):
                    emoji = "🟢" if ping < 80 else ("🟡" if ping < 150 else "🔴")
                    val   = f"{ping} ms" if ping < 9999 else "inalcançável"
                    linhas.append(f"{emoji} {nome}: {val}")
                self.ui_segura(lambda: self.lbl_servidores.configure(text="\n".join(linhas)))

            bs_server_ping.medir_todos_servidores(callback=_atualizar_parcial)
            self.ui_segura(lambda: self.btn_medir_srv.configure(
                text="📡 Medir Novamente", state="normal"
            ))

        threading.Thread(target=_worker, daemon=True).start()


    # ==================================================================
    # AÇÕES — VISUAL & TRACKER
    # ==================================================================

    def acionar_tela_cheia(self):
        ativado = self.sw_tela_cheia.get() == 1
        if ativado:
            threading.Thread(target=tela_cheia.forcar_tela_cheia, daemon=True).start()
        else:
            tela_cheia.reverter_tela_cheia()
        self.atualizar_ui_switch(self.sw_tela_cheia, ativado, "Forçar Tela Cheia Exclusiva")

    def acionar_resolucao(self):
        ativado = self.sw_resolucao.get() == 1
        if ativado:
            threading.Thread(target=resolucao.aplicar_resolucao_esticada, daemon=True).start()
        else:
            resolucao.reverter_resolucao()
        self.atualizar_ui_switch(self.sw_resolucao, ativado, "Forçar Resolução Esticada")

    def acionar_tracker(self):
        """
        Corrigido: usa overlay_pro.ativar_overlay / fechar_overlay.
        O fechar é feito via .after() agendado no loop do overlay — sem deadlock.
        """
        ativado = self.sw_tracker.get() == 1
        if ativado:
            overlay_pro.ativar_overlay()
        else:
            overlay_pro.fechar_overlay()
        self.atualizar_ui_switch(self.sw_tracker, ativado, "Monitor Hardware (Tracker)")

    # ==================================================================
    # AÇÕES — FERRAMENTAS PRO
    # ==================================================================

    def acionar_snaptap(self):
        ativado = self.sw_snaptap.get() == 1
        if ativado:
            threading.Thread(target=snaptap.iniciar_snaptap, daemon=True).start()
        else:
            snaptap.parar_snaptap()
        self.atualizar_ui_switch(self.sw_snaptap, ativado, "Teclado SnapTap (Software)")

    def acionar_unpark(self):
        ativado = self.sw_unpark.get() == 1
        if ativado:
            threading.Thread(target=unpark_cpu.acordar_nucleos, daemon=True).start()
        else:
            unpark_cpu.reverter_unpark()
        self.atualizar_ui_switch(self.sw_unpark, ativado, "Unpark CPU (Acordar Núcleos)")

    def acionar_servicos(self):
        ativado = self.sw_servicos.get() == 1
        if ativado:
            threading.Thread(target=servicos.otimizar_servicos, daemon=True).start()
        else:
            servicos.reverter_servicos()
        self.atualizar_ui_switch(self.sw_servicos, ativado, "Suspender Bloatware")

    def acionar_entrada(self):
        ativado = self.sw_entrada.get() == 1
        if ativado:
            threading.Thread(target=entrada_instantanea.otimizar_entrada, daemon=True).start()
        else:
            entrada_instantanea.reverter_entrada()
        self.atualizar_ui_switch(self.sw_entrada, ativado, "Skip Intro (Pular Abertura)")

    def acionar_audio_competitivo(self):

        ativado = self.sw_audio.get() == 1
        if ativado:
            def worker():
                sucesso, msg = audio_competitivo.aplicar_audio_competitivo()
                if sucesso:
                    messagebox.showinfo("🔊 Áudio Competitivo", msg)
            threading.Thread(target=worker, daemon=True).start()
        else:
            threading.Thread(target=audio_competitivo.reverter_audio_competitivo, daemon=True).start()
        self.atualizar_ui_switch(self.sw_audio, ativado, "🔊 Áudio Competitivo (Passos)")

    def acionar_fov(self, preset_nome):
        fov_valor = fov_helper.FOV_PRESETS.get(preset_nome, 90)
        def worker():
            sucesso, msg = fov_helper.aplicar_fov(fov_valor)
            if sucesso:
                self.ui_segura(lambda: messagebox.showinfo("📄 FOV Ajustado", msg))
        threading.Thread(target=worker, daemon=True).start()

    def acionar_backup_config(self):
        def worker():
            self.ui_segura(lambda: self.btn_backup.configure(text="⏳ Salvando..."))
            sucesso, msg, _ = bs_config_backup.criar_backup("otimizador")
            self.ui_segura(lambda: self.btn_backup.configure(text="💾 Backup Config BS"))
            self.ui_segura(lambda: messagebox.showinfo("Backup", msg))
        threading.Thread(target=worker, daemon=True).start()

    def acionar_restaurar_backup(self):
        backups = bs_config_backup.listar_backups()
        if not backups:
            messagebox.showwarning("Sem Backups", "Nenhum backup encontrado.\nCrie um backup primeiro.")
            return
        ultimo = backups[0]
        if messagebox.askyesno("Restaurar Backup",
                               f"Restaurar:\n{ultimo['nome']}\n({ultimo['data']})?"):
            def worker():
                self.ui_segura(lambda: self.btn_restaurar.configure(text="⏳ Restaurando..."))
                sucesso, msg = bs_config_backup.restaurar_backup(ultimo["caminho"])
                self.ui_segura(lambda: self.btn_restaurar.configure(text="📂 Restaurar Último Backup"))
                self.ui_segura(lambda: messagebox.showinfo("Restauração", msg))
            threading.Thread(target=worker, daemon=True).start()

    # ==================================================================
    # AÇÕES — STATS HUD
    # ==================================================================

    def acionar_stats_hud(self):
        """Ativa/desativa o overlay de Kill/HS/KD por cima do jogo."""
        ativado = self.sw_stats_hud.get() == 1
        if ativado:
            stats_hud.ativar_stats_hud()
        else:
            stats_hud.fechar_stats_hud()
        self.atualizar_ui_switch(self.sw_stats_hud, ativado, "Stats HUD (Overlay in-game)")

    # ==================================================================
    # MIRA
    # ==================================================================

    def mudar_cor_mira(self, cor):
        self.mira_cor = cor
        self.atualizar_mira_dinamica()

    def atualizar_mira_dinamica(self, _=None):
        mira.ativar_mira(self.mira_cor, self.seg_mira.get().lower())

    def desligar_mira(self):
        mira.desativar_mira()

    # ==================================================================
    # MONITOR DE PING
    # ==================================================================

    def iniciar_monitor_ping(self):
        def atualizar():
            try:
                ping = dns_ping.obter_ping_atual()
                cor  = CORES["verde_neon"] if ping < 60 else CORES["vermelho_neon"]
                self.lbl_ping_atual.configure(text=f"Ping Atual: {ping} ms", text_color=cor)
            except Exception:
                pass
            self.after(2000, atualizar)
        atualizar()

    # ==================================================================
    # HELPERS DE UI
    # ==================================================================

    def criar_titulo(self, frame_pai, texto):
        ctk.CTkLabel(
            frame_pai, text=texto,
            font=("Orbitron", 22, "bold"), text_color=CORES["roxo_destaque"]
        ).pack(anchor="w", pady=(25, 15), padx=40)

    def criar_botao_menu(self, texto, linha, nome):
        btn = ctk.CTkButton(
            self.sidebar, text=texto,
            font=("Inter", 14, "bold"), fg_color="transparent",
            text_color=CORES["texto_secundario"], hover_color=CORES["card_info"],
            anchor="w", height=45, corner_radius=10,
            command=lambda: self.selecionar_frame(nome)
        )
        btn.grid(row=linha, column=0, padx=15, pady=5, sticky="ew")
        return btn

    def criar_switch_com_info(self, container, texto, descricao, is_risky=False, command=None):
        row_frame = ctk.CTkFrame(container, fg_color="transparent")
        row_frame.pack(fill="x", pady=6, padx=10)

        cor_progresso = CORES["vermelho_neon"] if is_risky else CORES["verde_neon"]
        sw = ctk.CTkSwitch(
            row_frame, text=f"⚪ [OFF] {texto}",
            text_color=CORES["texto_secundario"],
            progress_color=cor_progresso,
            font=("Inter", 13, "bold"), command=command
        )
        sw.pack(side="left", anchor="w")

        ctk.CTkButton(
            row_frame, text="ℹ️", width=25, height=25,
            fg_color="transparent", text_color=CORES["texto_secundario"],
            hover_color=CORES["borda"],
            command=lambda: messagebox.showinfo(texto, descricao)
        ).pack(side="right", anchor="e")

        row_frame.switch = sw
        row_frame.get    = sw.get
        return row_frame

    def criar_botao_acao_com_info(self, container, texto, descricao, cor_base, cor_hover, side="top", command=None):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(side=side, fill="x", expand=True, padx=5, pady=5)

        btn = ctk.CTkButton(
            frame, text=texto,
            font=("Inter", 14, "bold"), fg_color=cor_base,
            hover_color=cor_hover, text_color="#fff",
            height=45, corner_radius=8, command=command
        )
        btn.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            frame, text="ℹ️", width=45, height=45,
            fg_color=CORES["card_info"], text_color=CORES["texto_secundario"],
            hover_color=CORES["borda"], corner_radius=8,
            command=lambda: messagebox.showinfo("Informação", descricao)
        ).pack(side="right", padx=(5, 0))

        return btn

    def selecionar_frame(self, nome):
        if self.frame_atual:
            self.frame_atual.grid_forget()

        frames = {
            "info":        self.frame_info,
            "desempenho":  self.frame_desempenho,
            "rede":        self.frame_rede,
            "visual":      self.frame_visual,
            "ferramentas": self.frame_ferramentas,
            "stats":       self.frame_stats,
        }
        self.frame_atual = frames[nome]
        self.frame_atual.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        botoes = [self.btn_info, self.btn_desempenho, self.btn_rede,
                  self.btn_visual, self.btn_ferramentas, self.btn_stats]
        for btn in botoes:
            btn.configure(fg_color="transparent", text_color=CORES["texto_secundario"])

        botoes_map = {
            "info":        self.btn_info,
            "desempenho":  self.btn_desempenho,
            "rede":        self.btn_rede,
            "visual":      self.btn_visual,
            "ferramentas": self.btn_ferramentas,
            "stats":       self.btn_stats,
        }
        botoes_map[nome].configure(fg_color=CORES["roxo_destaque"], text_color="#fff")

    def abrir_suporte_whatsapp(self):
        import webbrowser
        webbrowser.open("https://wa.me/5511999999999?text=Olá,%20preciso%20de%20suporte%20com%20o%20BS%20Optimizer%20Pro")


if __name__ == "__main__":
    import sys
    user = sys.argv[1] if len(sys.argv) > 1 else "Visitante"
    dias = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    App(username=user, dias_restantes=dias).mainloop()