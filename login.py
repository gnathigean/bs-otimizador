import customtkinter as ctk
from tkinter import messagebox
import subprocess
import platform
import json
import os

import banco_dados
import main 

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ==============================================================================
# GESTÃO DE ARQUIVOS OCULTOS E HWID
# ==============================================================================
def obter_caminho_config():
    """Cria uma pasta oculta no sistema do cliente para guardar o login (AppData)."""
    if platform.system() == "Windows":
        # Fica oculto em: C:\Users\Nome\AppData\Local\BSOptimizer
        pasta = os.path.join(os.getenv('LOCALAPPDATA'), 'BSOptimizer')
    else:
        # Fica oculto em: /home/gabriel/.bsoptimizer (Para os seus testes no Linux)
        pasta = os.path.join(os.path.expanduser('~'), '.bsoptimizer')
        
    if not os.path.exists(pasta):
        os.makedirs(pasta)
        
    return os.path.join(pasta, 'config_login.json')

ARQUIVO_CONFIG = obter_caminho_config()

def obter_hwid():
    """Gera o HWID lendo a Placa-Mãe. Se falhar, lê o Disco Rígido."""
    if platform.system() == "Windows":
        # O CREATE_NO_WINDOW impede que uma tela preta do CMD pisque na cara do cliente
        CREATE_NO_WINDOW = 0x08000000 
        
        try:
            # Plano A: Tenta obter o UUID da Placa-Mãe
            hwid = subprocess.check_output('wmic csproduct get uuid', creationflags=CREATE_NO_WINDOW).decode().split('\n')[1].strip()
            if hwid and hwid != "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF":
                return hwid
        except: pass
        
        try:
            # Plano B: Se a Placa-Mãe for bloqueada, pega o Serial do HD/SSD primário (C:)
            disco = subprocess.check_output('vol c:', creationflags=CREATE_NO_WINDOW).decode().split('\n')[1].strip()
            return disco
        except:
            return "HWID_DESCONHECIDO"
    else:
        return "DEV_LINUX_HWID" # Permite que você continue testando a interface no Ubuntu

# ==============================================================================
# INTERFACE GRÁFICA DE LOGIN
# ==============================================================================
class TelaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Blood Strike Optimizer Pro")
        self.centralizar_janela(420, 560)
        self.resizable(False, False)
        self.configure(fg_color="#101014")

        self.user_id_logado = None
        self.username_logado = None

        self.lbl_titulo = ctk.CTkLabel(self, text="⚡ BS OPTIMIZER", font=ctk.CTkFont(family="Impact", size=36, weight="bold"), text_color="#BB86FC")
        self.lbl_titulo.pack(pady=(50, 5))
        self.lbl_sub = ctk.CTkLabel(self, text="Painel de Acesso Exclusivo", font=("Roboto", 13), text_color="#8E8E93")
        self.lbl_sub.pack(pady=(0, 30))

        self.entry_user = ctk.CTkEntry(self, placeholder_text="👤 Nome de Usuário", width=280, height=45, font=("Roboto", 14), corner_radius=8, border_width=1, border_color="#3A3A55", fg_color="#1E1E26")
        self.entry_user.pack(pady=10)
        
        self.entry_senha = ctk.CTkEntry(self, placeholder_text="🔒 Senha de Acesso", width=280, height=45, font=("Roboto", 14), corner_radius=8, border_width=1, border_color="#3A3A55", fg_color="#1E1E26", show="•")
        self.entry_senha.pack(pady=10)

        self.frame_opcoes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_opcoes.pack(pady=10)

        self.var_salvar = ctk.BooleanVar()
        self.chk_salvar = ctk.CTkCheckBox(self.frame_opcoes, text="Lembrar-me", variable=self.var_salvar, font=("Roboto", 12), text_color="#EDEDF0", fg_color="#6200EE", border_width=2)
        self.chk_salvar.pack(side="left", padx=15)

        self.var_auto = ctk.BooleanVar()
        self.chk_auto = ctk.CTkCheckBox(self.frame_opcoes, text="Login Automático", variable=self.var_auto, font=("Roboto", 12), text_color="#EDEDF0", fg_color="#6200EE", border_width=2)
        self.chk_auto.pack(side="left", padx=15)

        self.btn_login = ctk.CTkButton(self, text="ENTRAR NA CONTA", width=280, height=45, font=("Roboto Bold", 14), fg_color="#6200EE", hover_color="#7B1FA2", corner_radius=8, command=self.efetuar_login)
        self.btn_login.pack(pady=(25, 15))

        self.lbl_aviso_site = ctk.CTkLabel(self, text="Não tem conta? Adquira no nosso site oficial.", font=("Roboto", 12), text_color="#8E8E93")
        self.lbl_aviso_site.pack(pady=(5, 0))

        self.frame_key = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_key = ctk.CTkEntry(self.frame_key, placeholder_text="🔑 Insira sua Chave de Acesso (Key)", width=280, height=45, font=("Roboto", 13), corner_radius=8, border_width=1, border_color="#3A3A55", fg_color="#1E1E26")
        self.entry_key.pack(pady=10)
        self.btn_ativar = ctk.CTkButton(self.frame_key, text="VALIDAR CHAVE", width=280, height=45, font=("Roboto Bold", 14), fg_color="#00C853", hover_color="#00E676", text_color="#101014", corner_radius=8, command=self.ativar_key)
        self.btn_ativar.pack(pady=10)

        self.carregar_configuracoes_locais()

    def centralizar_janela(self, largura, altura):
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura // 2)
        pos_y = (altura_tela // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    def carregar_configuracoes_locais(self):
        if os.path.exists(ARQUIVO_CONFIG):
            try:
                with open(ARQUIVO_CONFIG, "r") as f:
                    config = json.load(f)
                
                if config.get("salvar_senha"):
                    self.entry_user.insert(0, config.get("user", ""))
                    self.entry_senha.insert(0, config.get("senha", ""))
                    self.var_salvar.set(True)
                
                if config.get("login_auto"):
                    self.var_auto.set(True)
                    if config.get("user") and config.get("senha"):
                        self.btn_login.configure(text="AUTENTICANDO...", fg_color="#3f37c9")
                        self.after(500, self.efetuar_login)
            except: pass

    def guardar_configuracoes_locais(self, user, senha):
        salvar = self.var_salvar.get()
        auto = self.var_auto.get()
        dados = {
            "salvar_senha": salvar,
            "login_auto": auto,
            "user": user if salvar else "",
            "senha": senha if salvar else ""
        }
        with open(ARQUIVO_CONFIG, "w") as f:
            json.dump(dados, f)

    def efetuar_login(self):
        user = self.entry_user.get()
        senha = self.entry_senha.get()
        
        if not user or not senha:
            messagebox.showwarning("Aviso", "Por favor, preencha o usuário e a senha.")
            self.btn_login.configure(text="ENTRAR NA CONTA", fg_color="#6200EE")
            return
            
        hwid_maquina = obter_hwid()
        
        try:
            sucesso, user_id, msg = banco_dados.validar_login(user, senha, hwid_maquina)
        except Exception as e:
            messagebox.showerror("Sem Conexão", f"Não foi possível conectar ao servidor.\n{e}")
            self.btn_login.configure(text="ENTRAR NA CONTA", fg_color="#6200EE")
            return
        
        if sucesso:
            self.user_id_logado = user_id
            self.username_logado = user
            self.guardar_configuracoes_locais(user, senha)
            self.verificar_assinatura()
        else:
            messagebox.showerror("Acesso Negado", msg)
            self.btn_login.configure(text="ENTRAR NA CONTA", fg_color="#6200EE")
            self.var_auto.set(False)
            self.guardar_configuracoes_locais(user, senha)

    def verificar_assinatura(self):
        try:
            tem_licenca, dias_restantes = banco_dados.verificar_licenca_ativa(self.user_id_logado)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar a licença ativa:\n{e}")
            self.btn_login.configure(text="ENTRAR NA CONTA", fg_color="#6200EE")
            return
            
        if tem_licenca:
            self.destroy() 
            app = main.App(username=self.username_logado, dias_restantes=dias_restantes)
            app.mainloop()
        else:
            self.entry_user.pack_forget()
            self.entry_senha.pack_forget()
            self.frame_opcoes.pack_forget()
            self.btn_login.pack_forget()
            self.lbl_aviso_site.pack_forget()
            
            self.lbl_titulo.configure(text="🔒 LICENÇA INATIVA", font=("Impact", 28), text_color="#FF5252")
            self.lbl_sub.configure(text="O seu tempo de uso expirou ou não possui um plano ativo.")
            self.frame_key.pack(pady=10)
            
            self.var_auto.set(False)
            self.guardar_configuracoes_locais(self.username_logado, self.entry_senha.get())

    def ativar_key(self):
        chave = self.entry_key.get().strip()
        if not chave: 
            messagebox.showwarning("Aviso", "Insira uma chave válida no campo.")
            return
            
        try:
            sucesso, msg = banco_dados.ativar_key(self.user_id_logado, chave)
            if sucesso:
                messagebox.showinfo("Plano Ativado!", msg)
                self.verificar_assinatura() 
            else:
                messagebox.showerror("Chave Inválida", msg)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao validar a chave.\n{e}")

if __name__ == "__main__":
    app = TelaLogin()
    app.mainloop()