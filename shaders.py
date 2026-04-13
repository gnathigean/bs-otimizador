import os
import shutil
import platform
import time

def limpar_shaders():
    """Apaga fisicamente o cache de vídeo da NVIDIA, AMD e DirectX."""
    if platform.system() != "Windows":
        time.sleep(1.5)
        return "✅ (Simulação) Shaders gráficos apagados!"
    
    localappdata = os.environ.get('LOCALAPPDATA', '')
    
    # Pastas onde as placas de vídeo guardam o lixo de processamento gráfico
    caminhos_alvo = [
        os.path.join(localappdata, 'NVIDIA', 'DXCache'),
        os.path.join(localappdata, 'NVIDIA', 'GLCache'),
        os.path.join(localappdata, 'AMD', 'DxCache'),
        os.path.join(localappdata, 'D3DSCache') # DirectX genérico
    ]
    
    arquivos_apagados = 0
    
    for pasta in caminhos_alvo:
        if os.path.exists(pasta):
            for item in os.listdir(pasta):
                caminho_completo = os.path.join(pasta, item)
                try:
                    if os.path.isfile(caminho_completo):
                        os.remove(caminho_completo)
                    elif os.path.isdir(caminho_completo):
                        shutil.rmtree(caminho_completo)
                    arquivos_apagados += 1
                except:
                    pass # O arquivo pode estar em uso pelo Windows no momento
                    
    return f"✅ Shaders limpos com sucesso! ({arquivos_apagados} ficheiros apagados)"