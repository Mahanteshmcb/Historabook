import os
from diffusers.pipelines.auto_pipeline import AutoPipelineForText2Image
import torch

# Save exactly where the app is looking
model_path = "./local_models/sd-turbo"

print(f"⏳ Downloading/Copying SD-Turbo to: {model_path}")

# This will fetch from HuggingFace (or your cache) and save it locally
pipe = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/sd-turbo", 
    torch_dtype=torch.float16, 
    variant="fp16"
)
pipe.save_pretrained(model_path)
print("✅ Success! Visual Model is now inside your project.")