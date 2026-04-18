import customtkinter as ctk
from tkinter import messagebox
import subprocess
import platform
import json
import os

import requests
import sys

ctk.set_appearance_mode("dark")

# URL da API (Mude para a URL do Render após o deploy)
API_BASE_URL = "https://bs-optimizer-api.onrender.com"

# ==============================================================================
# GESTÃO DE ARQUIVOS OCULTOS E HWID
# ==============================================================================
def obter_caminho_config():
    if platform.system() == "Windows":
        pasta = os.path.join(os.getenv('LOCALAPPDATA'), 'BSOptimizer')
    else:
        pasta = os.path.join(os.path.expanduser('~'), '.bsoptimizer')
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    return os.path.join(pasta, 'config_login.json')

ARQUIVO_CONFIG = obter_caminho_config()

def obter_hwid():
    if platform.system() == "Windows":
        CREATE_NO_WINDOW = 0x08000000 
        try:
            hwid = subprocess.check_output('wmic csproduct get uuid', creationflags=CREATE_NO_WINDOW).decode().split('\n')[1].strip()
            if hwid and hwid != "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF": return hwid
        except Exception: pass
        try:
            disco = subprocess.check_output('vol c:', creationflags=CREATE_NO_WINDOW).decode().split('\n')[1].strip()
            return disco
        except Exception: return "HWID_DESCONHECIDO"
    else:
        return "DEV_LINUX_HWID" 

# ==============================================================================
# INTERFACE DE LOGIN PREMIUM
# ==============================================================================
class TelaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("BS Optimizer Pro | Elite Access")
        self.centralizar_janela(400, 550)
        self.resizable(False, False)
        
        # Cores idênticas ao Site
        self.configure(fg_color="#050508") # Fundo super escuro
        
        self.user_id_logado = None
        self.username_logado = None
        self.login_sucesso = False
        self.dias_restantes = 0

        self.lbl_titulo = ctk.CTkLabel(self, text="⚡ BS OPTIMIZER", font=ctk.CTkFont(family="Impact", size=34, weight="bold"), text_color="#8b5cf6")
        self.lbl_titulo.pack(pady=(50, 5))
        self.lbl_sub = ctk.CTkLabel(self, text="Painel de Acesso Exclusivo", font=("Inter", 13), text_color="#94a3b8")
        self.lbl_sub.pack(pady=(0, 35))

        self.entry_user = ctk.CTkEntry(self, placeholder_text="👤 Nome de Usuário", width=280, height=45, font=("Inter", 14), corner_radius=10, border_width=1, border_color="#1E1E2E", fg_color="#12121A", text_color="#f8fafc")
        self.entry_user.pack(pady=10)
        
        self.entry_senha = ctk.CTkEntry(self, placeholder_text="🔒 Senha de Acesso", width=280, height=45, font=("Inter", 14), corner_radius=10, border_width=1, border_color="#1E1E2E", fg_color="#12121A", text_color="#f8fafc", show="•")
        self.entry_senha.pack(pady=10)

        self.frame_opcoes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_opcoes.pack(pady=12)

        self.var_salvar = ctk.BooleanVar()
        self.chk_salvar = ctk.CTkCheckBox(self.frame_opcoes, text="Lembrar-me", variable=self.var_salvar, font=("Inter", 12), text_color="#94a3b8", fg_color="#8b5cf6", hover_color="#a855f7", border_color="#8b5cf6", border_width=2)
        self.chk_salvar.pack(side="left", padx=10)

        self.var_auto = ctk.BooleanVar()
        self.chk_auto = ctk.CTkCheckBox(self.frame_opcoes, text="Auto Login", variable=self.var_auto, font=("Inter", 12), text_color="#94a3b8", fg_color="#8b5cf6", hover_color="#a855f7", border_color="#8b5cf6", border_width=2)
        self.chk_auto.pack(side="left", padx=10)

        self.btn_login = ctk.CTkButton(self, text="ENTRAR NA CONTA", width=280, height=45, font=("Inter", 14, "bold"), fg_color="#8b5cf6", hover_color="#a855f7", text_color="#ffffff", corner_radius=10, command=self.efetuar_login)
        self.btn_login.pack(pady=(20, 15))

        self.lbl_aviso_site = ctk.CTkLabel(self, text="Não tem conta? Crie no site oficial.", font=("Inter", 12), text_color="#555555")
        self.lbl_aviso_site.pack(pady=(5, 0))

        # Painel de Licença (Inativo por padrão)
        self.frame_key = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_key = ctk.CTkEntry(self.frame_key, placeholder_text="🔑 Insira sua Key (16 Dígitos)", width=280, height=45, font=("Consolas", 13), corner_radius=10, border_width=1, border_color="#1E1E2E", fg_color="#12121A")
        self.entry_key.pack(pady=10)
        self.btn_ativar = ctk.CTkButton(self.frame_key, text="VALIDAR CHAVE PIX", width=280, height=45, font=("Inter", 14, "bold"), fg_color="#00e676", hover_color="#00c853", text_color="#050508", corner_radius=10, command=self.ativar_key)
        self.btn_ativar.pack(pady=10)

        self.carregar_configuracoes_locais()

    def centralizar_janela(self, largura, altura):
        pos_x = (self.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.winfo_screenheight() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    def carregar_configuracoes_locais(self):
        if os.path.exists(ARQUIVO_CONFIG):
            try:
                with open(ARQUIVO_CONFIG, "r") as f: config = json.load(f)
                if config.get("salvar_senha"):
                    self.entry_user.insert(0, config.get("user", ""))
                    self.entry_senha.insert(0, config.get("senha", ""))
                    self.var_salvar.set(True)
                if config.get("login_auto"):
                    self.var_auto.set(True)
                    if config.get("user") and config.get("senha"):
                        self.btn_login.configure(text="AUTENTICANDO...", fg_color="#a855f7")
                        self.after(500, self.efetuar_login)
            except: pass

    def guardar_configuracoes_locais(self, user, senha):
        salvar = self.var_salvar.get()
        dados = {
            "salvar_senha": salvar,
            "login_auto": self.var_auto.get(),
            "user": user if salvar else "",
            "senha": senha if salvar else ""
        }
        with open(ARQUIVO_CONFIG, "w") as f: json.dump(dados, f)

    def efetuar_login(self):
        user, senha = self.entry_user.get(), self.entry_senha.get()
        if not user or not senha:
            messagebox.showwarning("Aviso", "Preencha o usuário e a senha.")
            self.btn_login.configure(text="ENTRAR NA CONTA", fg_color="#8b5cf6")
            return

        self.btn_login.configure(text="AUTENTICANDO...", fg_color="#a855f7", state="disabled")
        import threading
        threading.Thread(target=self._thread_login, args=(user, senha), daemon=True).start()

    def _thread_login(self, user, senha):
        hwid_maquina = obter_hwid()
        try:
            response = requests.post(f"{API_BASE_URL}/api/desktop/login", json={
                "username": user,
                "password": senha,
                "hwid": hwid_maquina
            }, timeout=10)
            dados = response.json()
            sucesso = dados.get("sucesso")
            user_id = dados.get("user_id")
            msg = dados.get("mensagem")
            
            if sucesso:
                self.after(0, lambda: self._pos_login_ok(user_id, user, senha))
            else:
                self.after(0, lambda: self._pos_login_erro("Acesso Negado", msg, user, senha))
        except Exception as e:
            self.after(0, lambda: self._pos_login_erro("Sem Conexão", f"Erro de rede.\n{e}", user, senha))

    def _pos_login_ok(self, user_id, user, senha):
        self.user_id_logado = user_id
        self.username_logado = user
        self.guardar_configuracoes_locais(user, senha)
        self.verificar_assinatura()

    def _pos_login_erro(self, titulo, msg, user, senha):
        messagebox.showerror(titulo, msg)
        self.btn_login.configure(text="ENTRAR NA CONTA", fg_color="#8b5cf6", state="normal")
        self.var_auto.set(False)
        self.guardar_configuracoes_locais(user, senha)

    def verificar_assinatura(self):
        self.btn_login.configure(text="VERIFICANDO LICENÇA...", state="disabled", fg_color="#a855f7")
        import threading
        threading.Thread(target=self._thread_assinatura, daemon=True).start()

    def _thread_assinatura(self):
        try:
            response = requests.post(f"{API_BASE_URL}/api/desktop/licenca", json={
                "user_id": self.user_id_logado
            }, timeout=10)
            dados = response.json()
            tem_licenca = dados.get("tem_licenca")
            dias_restantes = dados.get("dias_restantes")
            self.after(0, lambda: self._pos_assinatura(tem_licenca, dias_restantes))
        except Exception as e:
            self.after(0, lambda: self._pos_assinatura_erro(e))

    def _pos_assinatura(self, tem_licenca, dias_restantes):
        self.btn_login.configure(state="normal")
        if tem_licenca:
            self.login_sucesso = True
            self.dias_restantes = dias_restantes
            self.quit()
        else:
            self.entry_user.pack_forget()
            self.entry_senha.pack_forget()
            self.frame_opcoes.pack_forget()
            self.btn_login.pack_forget()
            self.lbl_aviso_site.pack_forget()
            self.lbl_titulo.configure(text="🔒 LICENÇA INATIVA", text_color="#ff3a3a")
            self.lbl_sub.configure(text="Plano expirado. Insira sua Key do Mercado Pago.")
            self.frame_key.pack(pady=20)
            self.var_auto.set(False)
            self.guardar_configuracoes_locais(self.username_logado, self.entry_senha.get())

    def _pos_assinatura_erro(self, e):
        messagebox.showerror("Erro", f"Erro ao verificar a licença.\n{e}")
        self.btn_login.configure(text="ENTRAR NA CONTA", fg_color="#8b5cf6", state="normal")

    def ativar_key(self):
        chave = self.entry_key.get().strip()
        if not chave: return messagebox.showwarning("Aviso", "Insira uma chave.")
        try:
            response = requests.post(f"{API_BASE_URL}/api/desktop/ativar", json={
                "user_id": self.user_id_logado,
                "key": chave
            }, timeout=10)
            dados = response.json()
            sucesso = dados.get("sucesso")
            msg = dados.get("mensagem")
            
            if sucesso:
                messagebox.showinfo("Sucesso!", msg)
                self.verificar_assinatura() 
            else: messagebox.showerror("Inválida", msg)
        except Exception as e: messagebox.showerror("Erro", f"Falha na validação.\n{e}")

if __name__ == "__main__":
    app = TelaLogin()
    app.mainloop()
    if getattr(app, "login_sucesso", False):
        user = app.username_logado
        dias = app.dias_restantes
        app.destroy()
        
        import subprocess
        # Inicia o app principal em um processo limpo, evitando bugs de múltiplos Tk loop
        subprocess.Popen([sys.executable, "main.py", user, str(dias)])
        sys.exit(0)