import torch
import GPUtil
import numpy as np
import os
from dotenv import load_dotenv

print("--- JARVIS WSL VALIDATION ---")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"CUDA Version: {torch.version.cuda}")

try:
    gpus = GPUtil.getGPUs()
    if gpus:
        print(f"GPUtil Detected: {gpus[0].name} (Temp: {gpus[0].temperature}C)")
except Exception as e:
    print(f"GPUtil Error: {e}")

print(f"Numpy Version: {np.__version__}")
print(f"Current PID: {os.getpid()}")
print("--- VALIDATION COMPLETE ---")
