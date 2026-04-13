import platform
import ctypes

def definir_05ms():
    """Ajusta a resolução do timer do Windows para 0.5ms."""
    if platform.system() != "Windows":
        return True, "✅ (Simulação) Timer ajustado para 0.5ms!"

    try:
        # Carrega a DLL do sistema para manipular o relógio do Kernel
        ntdll = ctypes.WinDLL('ntdll.dll')
        # 0.5ms em unidades de 100ns é 5000
        res = ctypes.c_ulong(5000)
        # NtSetTimerResolution(Desejado, Setar?, Atual)
        ntdll.NtSetTimerResolution(res, 1, ctypes.byref(ctypes.c_ulong()))
        return True, "✅ Timer Resolution: 0.5ms Ativado!"
    except Exception as e:
        return False, f"⚠️ Erro no Timer: {e}"

def resetar_timer():
    if platform.system() != "Windows":
        return True, "Timer Resolution Nativo • Forçar 0.500 ms"
    
    try:
        ntdll = ctypes.WinDLL('ntdll.dll')
        ntdll.NtSetTimerResolution(ctypes.c_ulong(156250), 0, ctypes.byref(ctypes.c_ulong()))
        return True, "Timer Resolution Nativo • Forçar 0.500 ms"
    except:
        return False, "Timer Resolution Nativo • Forçar 0.500 ms"