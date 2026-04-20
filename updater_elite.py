import requests
import os
import sys
import subprocess
import threading
import customtkinter as ctk
from tkinter import messagebox

# Configurações do Repositório (Altere conforme seu GitHub)
GITHUB_USER = "gnathigean"
GITHUB_REPO = "bs-otimizador"
VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.json"

class UpdaterUI(ctk.CTkToplevel):
    def __init__(self, parent, download_url, nova_versao):
        super().__init__(parent)
        self.title("🔥 Atualização Elite Disponível")
        self.geometry("400x250")
        self.resizable(False, False)
        self.download_url = download_url
        self.nova_versao = nova_versao
        self.parent = parent
        
        # Garante que a janela fique por cima
        self.attributes("-topmost", True)
        self.grab_set()
        
        self.configure(fg_color="#050508")
        
        self.lbl = ctk.CTkLabel(
            self, text=f"🚀 Nova Versão {nova_versao} Encontrada!",
            font=("Orbitron", 16, "bold"), text_color="#8B5CF6"
        )
        self.lbl.pack(pady=(30, 10))
        
        self.info = ctk.CTkLabel(
            self, text="O sistema está baixando os novos módulos\nde performance. Não feche o programa.",
            font=("Inter", 12), text_color="#94A3B8"
        )
        self.info.pack(pady=10)
        
        self.progress = ctk.CTkProgressBar(self, width=300, progress_color="#00E676")
        self.progress.set(0)
        self.progress.pack(pady=20)
        
        self.lbl_status = ctk.CTkLabel(self, text="Iniciando download...", font=("Inter", 10))
        self.lbl_status.pack()
        
        # Inicia o download em thread separada
        threading.Thread(target=self.executar_download, daemon=True).start()

    def executar_download(self):
        try:
            local_filename = "BS_Optimizer_Novo.exe" if getattr(sys, 'frozen', False) else "main_novo.py"
            
            with requests.get(self.download_url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                p = downloaded / total_size
                                self.progress.set(p)
                                self.lbl_status.configure(text=f"Baixando: {int(p*100)}%")
            
            self.lbl_status.configure(text="✅ Download concluído! Reiniciando...", text_color="#00E676")
            self.after(2000, self.aplicar_substituicao)
            
        except Exception as e:
            messagebox.showerror("Erro no Update", f"Falha ao baixar atualização: {e}")
            self.destroy()

    def aplicar_substituicao(self):
        """Cria o script de substituição e fecha o app."""
        exe_atual = os.path.basename(sys.executable) if getattr(sys, 'frozen', False) else "main.py"
        novo_arquivo = "BS_Optimizer_Novo.exe" if getattr(sys, 'frozen', False) else "main_novo.py"
        
        # Script .bat para Windows realizar a troca com o app fechado
        with open("update.bat", "w") as f:
            f.write(f"@echo off\n")
            f.write(f"timeout /t 2 /nobreak > nul\n")
            f.write(f"del /f /q \"{exe_atual}\"\n")
            f.write(f"ren \"{novo_arquivo}\" \"{exe_atual}\"\n")
            f.write(f"start \"\" \"{exe_atual}\"\n")
            f.write(f"del \"%~f0\"\n") # Se auto-deleta
            
        subprocess.Popen("update.bat", shell=True)
        os._exit(0)

def verificar_atualizacao(janela_pai, versao_atual):
    """
    Verifica se existe uma nova versão no GitHub.
    Se existir, abre a UI de download.
    """
    try:
        response = requests.get(VERSION_URL, timeout=5)
        if response.status_code == 200:
            dados = response.json()
            nova_versao = str(dados.get("versao"))
            download_url = dados.get("url")
            
            if float(nova_versao) > float(versao_atual):
                UpdaterUI(janela_pai, download_url, nova_versao)
                return True
        return False
    except Exception:
        return False
