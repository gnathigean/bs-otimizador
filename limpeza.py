import os
import shutil

def executar_limpeza():
    """Limpa as pastas temporárias do Windows e retorna a quantidade de arquivos apagados."""
    pastas_alvo = [
        os.environ.get('TEMP'), 
        r'C:\Windows\Temp',     
        r'C:\Windows\Prefetch'  
    ]
    
    arquivos_excluidos = 0
    
    for pasta in pastas_alvo:
        if not pasta or not os.path.exists(pasta):
            continue
            
        for item in os.listdir(pasta):
            caminho = os.path.join(pasta, item)
            try:
                if os.path.isfile(caminho) or os.path.islink(caminho):
                    os.unlink(caminho)
                elif os.path.isdir(caminho):
                    shutil.rmtree(caminho)
                arquivos_excluidos += 1
            except Exception:
                pass 
                
    return arquivos_excluidos