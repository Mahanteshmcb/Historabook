# Historabook: Interactive Multimodal Teaching Assistant

**Overview:** Historabook is an open-source, offline-capable AI system that reads, understands, and teaches any book or document. It features multi-speaker narration, real-time interactive voice Q&A (RAG), and generates contextual visual drafts (using SD-Turbo) for every lesson segment.

## 🚀 Final MVP Status (Day 31 Complete)

You have successfully built the full MVP (Minimum Viable Product).

| Feature | Status | Notes |
| :--- | :--- | :--- |
| **LLM Planner** | ✅ **Active** | Phi-3 LLM generates structured, multi-segment lesson plans. |
| **Visuals (Tier A)** | ✅ **Active** | SD-Turbo runs on GPU via VRAM Swapper, generating low-latency image drafts. |
| **Audio/Voice** | ✅ **Active** | Piper TTS (realistic voice) and Whisper ASR (microphone input) are fully integrated. |
| **Intelligence Core** | ✅ **Active** | FAISS Vector Store enables context-aware answering (RAG). |

---

## 🛠️ Tech Stack & Components

| Component | Tool / Model | License |
| :--- | :--- | :--- |
| **Orchestration** | FastAPI, Python 3.10+ | MIT |
| **Database** | PostgreSQL (via Docker) | PostgreSQL |
| **Vector DB** | FAISS, Sentence Transformers | MIT / Apache 2.0 |
| **LLM/Brain** | Phi-3 Mini (GGUF) | MIT |
| **TTS/Voice** | Piper TTS (ONNX) | MIT |
| **ASR/Ears** | OpenAI Whisper | MIT |
| **Visuals** | SD-Turbo, Diffusers | Stability AI (Open RAIL++-M) |

---

## ⚙️ Installation & Setup Guide (RTX 4050 Optimized)

### **Prerequisites**

1.  **Python 3.10 or 3.11:** Required for stable PyTorch/CUDA linking (Python 3.13 is incompatible).
2.  **Docker Desktop:** Running (for Postgres and Redis).
3.  **FFmpeg:** Installed and accessible in the system PATH (required for Whisper).

### **Step 1: Create a Stable Python Environment**

*You must create a new environment to resolve the Python 3.13/PyTorch conflict.*

```powershell
# 1. Create Python 3.10 environment
conda create -n historabook_env python=3.10 -y

# 2. Activate it
conda activate historabook_env

# 3. connect docker and run 
docker login
docker compose up -d

# 4. Move to backend directory
cd backend

#  Run in Terminal
uvicorn main:app --reload --port 8001