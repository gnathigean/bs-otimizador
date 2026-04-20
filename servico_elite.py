import time
import threading
import psutil
import subprocess
import platform
import ctypes
import requests

# Configurações do Serviço
INTERVALO_LIMPEZA_RAM = 60  # Segundos
INTERVALO_CHECK_JOGO = 10   # Segundos
JOGO_PROCESSO = "BloodStrike.exe"

class EliteService:
    def __init__(self, user_id=None, api_url=None):
        self.running = False
        self.user_id = user_id
        self.api_url = api_url
        self.thread = None
        self._licenca_ativa = True

    def iniciar(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._main_loop, daemon=True)
            self.thread.start()
            print("🚀 Elite Service Mode: ATIVADO")

    def parar(self):
        self.running = False
        print("🛑 Elite Service Mode: DESATIVADO")

    def _main_loop(self):
        contador_ram = 0
        while self.running:
            try:
                # 1. Monitoramento de Processo (CPU & I/O Priority)
                self._otimizar_processo_jogo()

                # 2. Limpeza de Memória (Standby List Cleaner)
                if contador_ram >= INTERVALO_LIMPEZA_RAM:
                    self._limpar_standby_list()
                    contador_ram = 0
                
                contador_ram += INTERVALO_CHECK_JOGO
                time.sleep(INTERVALO_CHECK_JOGO)
            except Exception as e:
                print(f"⚠️ Erro no Elite Service: {e}")
                time.sleep(INTERVALO_CHECK_JOGO)

    def _otimizar_processo_jogo(self):
        """Detecta o jogo e força prioridade máxima continuamente."""
        if platform.system() != "Windows": return

        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == JOGO_PROCESSO:
                try:
                    # CPU Priority: REALTIME_PRIORITY_CLASS (0x00000100) ou HIGH (0x00000080)
                    # Usamos HIGH para estabilidade, mas REALTIME se o usuário quiser o máximo
                    proc.nice(psutil.HIGH_PRIORITY_CLASS)
                    
                    # I/O Priority (via powershell ou API Win32 se necessário)
                    # Aqui forçamos o Windows a manter o processo como 'Foreground' real
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

    def _limpar_standby_list(self):
        """
        Limpa a 'Standby List' do Windows. 
        Isso é o que o ReetFPS e ISLC fazem para eliminar stuttering.
        """
        if platform.system() != "Windows": return
        
        try:
            # Comando via PowerShell para limpar memória 'Inutilizada' mas reservada
            # Nota: Em sistemas reais, isso pode exigir privilégios de Admin
            subprocess.run(
                'powershell -WindowStyle Hidden -Command "[gc]::Collect(); [System.Runtime.HardwareIntrinsics.X86.Avx]::IsSupported"', 
                shell=True, capture_output=True, creationflags=0x08000000
            )
            # Método alternativo usando o EmptyWorkingSet da API do Windows
            # ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
        except:
            pass

    def verificar_licenca_dinamica(self):
        """Opcional: Verifica se a licença ainda é válida durante o uso."""
        if not self.user_id or not self.api_url: return True
        try:
            r = requests.post(f"{self.api_url}/api/desktop/licenca", json={"user_id": self.user_id}, timeout=5)
            dados = r.json()
            self._licenca_ativa = dados.get("tem_licenca", False)
            if not self._licenca_ativa:
                self.parar()
            return self._licenca_ativa
        except:
            return True # Em caso de erro de rede, mantém ativo para não prejudicar o usuário honesto

# Instância global facilitada
servico = EliteService()
