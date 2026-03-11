import gc
import os
import psutil
import time

def stabilize_system():
    print("[INIT] Protocolo de Estabilizacao...")
    
    try:
        p = psutil.Process(os.getpid())
        p.nice(psutil.NORMAL_PRIORITY_CLASS)
        print("[SAFE] Prioridade Windows: NORMAL.")
    except: pass
    
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("[SAFE] Cache PyTorch/CUDA limpo.")
    except ImportError: pass
    
    try:
        import cupy as cp
        cp.get_default_memory_pool().free_all_blocks()
        print("[SAFE] Cache CuPy limpo.")
    except ImportError: pass

    gc.collect()
    print("[SAFE] Garbage Collection concluido.")
    
    time.sleep(2)
    ram = psutil.virtual_memory().percent
    print(f"[METRIC] Uso de RAM: {ram}%")
    print("[FINISH] Sistema Estabilizado.")

if __name__ == "__main__":
    stabilize_system()
