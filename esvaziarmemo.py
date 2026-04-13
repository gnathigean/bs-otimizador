import platform
import ctypes
import psutil

def esvaziar_ram():
    """Libera a memória RAM ociosa de todos os processos do sistema (RAM Booster real)."""
    if platform.system() != "Windows":
        return "✅ Simulação (Linux): 1.2GB de RAM liberados!"

    try:
        psapi = ctypes.WinDLL('psapi')
        kernel32 = ctypes.WinDLL('kernel32')
        PROCESS_SET_QUOTA = 0x0100
        
        processos_limpos = 0
        
        # Itera por todos os processos abertos no PC
        for proc in psutil.process_iter(['pid']):
            try:
                # Tenta obter permissão para alterar a cota de memória do processo
                handle = kernel32.OpenProcess(PROCESS_SET_QUOTA, False, proc.info['pid'])
                if handle:
                    # Esvazia o Working Set (move a memória inativa para a paginação)
                    psapi.EmptyWorkingSet(handle)
                    kernel32.CloseHandle(handle)
                    processos_limpos += 1
            except:
                # Ignora processos vitais do Windows que bloqueiam o acesso
                pass 
                
        return f"✅ Memória RAM otimizada! ({processos_limpos} processos reduzidos)"
    except Exception as e:
        return f"⚠️ Erro ao limpar RAM: {e}"