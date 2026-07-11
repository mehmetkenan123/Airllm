# AirLLM Studio v2.0 - Professional Edition

**A professional, lightweight local LLM interface designed as a high-performance alternative to LM Studio.**

## 🚀 Features

- **Modern UI**: Three-panel layout (Model List, Chat Area, System Settings) inspired by VS Code and LM Studio
- **Streaming Responses**: Real-time token generation display with smooth typing animation
- **System Monitoring**: Live CPU, RAM, and estimated VRAM usage tracking
- **Model Management**: Easy switching between popular models (Qwen, Llama 3, Phi-3, Mistral)
- **Advanced Settings**: Adjustable GPU layers, temperature, and max tokens
- **Live Logs**: Real-time operation logs for debugging and monitoring
- **Dark Theme**: Professional VS Code / LM Studio inspired appearance
- **Low Resource Usage**: Optimized backend for minimal overhead

## 📸 Interface Overview

The application features a dark-themed, professional interface:

- **Left Sidebar**: List of available models with size and type info, plus chat history
- **Center Panel**: Chat history with distinct user/AI message styling and welcome screen
- **Right Panel**: Tabbed interface with:
  - **Settings Tab**: GPU layers, temperature, max tokens sliders
  - **System Tab**: Real-time RAM, CPU, and VRAM usage with visual bars
  - **Logs Tab**: Live operation logs with timestamp and level indicators

## 🛠️ Installation & Usage

### Prerequisites

- **Python 3.8+** installed and added to PATH

### Quick Start (Windows)

1. Download the project folder
2. Double-click `run.bat`
   - This script automatically installs dependencies (`flask`, `flask-cors`, `psutil`) if missing
   - It launches the application and opens your default browser

### Manual Start

```bash
pip install flask flask-cors psutil
python main.py
```

## ⚙️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the single-page application |
| `/api/models` | GET | Returns list of available models |
| `/api/system` | GET | Returns current CPU/RAM usage stats |
| `/api/logs` | GET | Returns live operation logs |
| `/api/log` | POST | Add a new log entry |
| `/api/chat` | POST | Streams chat completions based on prompt and settings |

## 🎨 Key Features Explained

### Streaming Chat
Messages are displayed token-by-token as they are generated, providing immediate feedback and a natural conversation flow.

### System Monitoring
- **RAM Usage**: Shows current memory utilization percentage
- **CPU Usage**: Real-time processor load
- **VRAM Estimate**: Calculated based on GPU layers setting

### Model Configuration
- **GPU Layers**: Control how many model layers are offloaded to GPU (0-100)
- **Temperature**: Adjust response creativity (0.1 = focused, 2.0 = creative)
- **Max Tokens**: Limit response length (128-4096)

## 📝 Note

This version uses a **simulated AI engine** for demonstration stability. In a production environment, the `AirLLMEngine` class in `main.py` would be replaced with actual `airllm` or `transformers` logic to load real GGUF/PyTorch models.

To enable real AI inference:
```bash
pip install airllm torch transformers
```

## 📄 License

MIT License

---

**Version**: 2.0 Professional Edition  
**Language**: English (International)  
**Platform**: Windows / Cross-platform
