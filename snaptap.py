import platform
import threading
import time

snaptap_rodando = False

def logica_snaptap():
    """Lógica real de SOCD: Anula a tecla oposta instantaneamente."""
    import keyboard
    global snaptap_rodando
    
    while snaptap_rodando:
        # Se as duas estiverem pressionadas, soltamos as duas para anular o atraso (Strafe Neutro)
        if keyboard.is_pressed('a') and keyboard.is_pressed('d'):
            keyboard.release('a')
            keyboard.release('d')
        # Pausa micro-segundos para não fritar o processador do PC
        time.sleep(0.001)

def iniciar_snaptap():
    global snaptap_rodando
    if platform.system() != "Windows":
        time.sleep(1)
        snaptap_rodando = True
        return True, "✅ (Simulação) SnapTap Injetado!"
    
    try:
        import keyboard # Verifica se a biblioteca está instalada
        if not snaptap_rodando:
            snaptap_rodando = True
            threading.Thread(target=logica_snaptap, daemon=True).start()
        return True, "✅ SnapTap SOCD Injetado! (Risco de Banimento)"
    except ImportError:
        return False, "⚠️ Erro: Instale a biblioteca (pip install keyboard)"
    except Exception as e:
        return False, f"⚠️ Erro no SnapTap: {e}"

def parar_snaptap():
    global snaptap_rodando
    snaptap_rodando = False
    return True, "Teclado SnapTap (Software SOCD)"