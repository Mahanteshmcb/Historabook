import torch 
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
else:
    print("❌ PyTorch cannot find the NVIDIA GPU. You need to reinstall PyTorch.")