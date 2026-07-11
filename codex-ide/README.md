# Codex IDE

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)](https://www.typescriptlang.org/)
[![Electron](https://img.shields.io/badge/Electron-28+-47848F?logo=electron)](https://www.electronjs.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)](https://react.dev/)

**A fully open-source, offline-capable IDE powered by local LLMs.**

Codex IDE is designed to run smoothly on low-end hardware (4GB RAM, Intel HD Graphics, dual-core CPUs) while providing powerful AI-assisted coding features using local language models.

## ✨ Features

### 🤖 Local AI Integration
- **AirLLM Backend**: Layer-by-layer offloading for running 7B+ models on 4GB RAM
- **llama.cpp WASM Fallback**: Browser-compatible inference
- **Multiple Model Support**: Qwen, Llama, CodeLlama, DeepSeek, Mistral, Phi-3
- **Offline First**: All AI features work without internet after initial setup

### 🚀 Performance Optimized
- **Low Memory Footprint**: <300MB idle, <2GB with AI model loaded
- **Fast Startup**: Cold start <3s, warm start <1s
- **Smart Caching**: LRU + semantic caching for responses
- **Background Loading**: AI models load without blocking the editor

### 💻 Full IDE Features
- **Monaco Editor Core**: Same editor as VS Code
- **Language Server Protocol**: Full LSP support for IntelliSense
- **Git Integration**: Built-in Git with visual diff and merge tools
- **Terminal**: xterm.js integrated terminal with AI suggestions
- **Search & Indexing**: SQLite FTS5 full-text search, ripgrep integration
- **Extension System**: VS Code compatible extension API

### 🔒 Privacy First
- **No Telemetry**: Zero data sent to external servers
- **Local Processing**: All AI inference happens on your machine
- **Sensitive Data Filtering**: Automatic detection and masking
- **Open Source**: Fully auditable codebase

## 🏗️ Architecture

```
codex-ide/
├── apps/
│   ├── desktop/          # Electron main application
│   ├── web/              # Optional web version
│   └── cli/              # Command-line interface
├── packages/
│   ├── core/             # Core utilities and types
│   ├── editor/           # Monaco Editor wrapper
│   ├── ai-core/          # AI abstraction layer
│   ├── ai-backends/      # AirLLM, llama.cpp, WebLLM
│   ├── model-manager/    # Model download and management
│   ├── indexing/         # Code indexing and embedding
│   ├── lsp-client/       # Language Server Protocol
│   ├── terminal/         # Terminal integration
│   ├── git/              # Git integration
│   ├── search/           # Search functionality
│   ├── ui/               # Shared UI components
│   ├── themes/           # Theme engine
│   └── extensions/       # Extension system
└── ...
```

## 🚀 Quick Start

### Prerequisites
- Node.js >= 20.0.0
- pnpm >= 9.0.0
- Python 3.11+ (optional, for some AI backends)

### Installation

```bash
# Clone the repository
git clone https://github.com/codex-ide/codex-ide.git
cd codex-ide

# Install dependencies
pnpm install

# Start development mode
pnpm dev

# Build for production
pnpm build
```

### Download Models

```bash
# Download default models (Qwen-1.5B, Phi-3-mini)
./scripts/download-default-models.sh
```

## 📦 Available Scripts

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start development mode |
| `pnpm build` | Build all packages |
| `pnpm test` | Run tests |
| `pnpm lint` | Run linter |
| `pnpm format` | Format code |
| `pnpm electron:dev` | Start Electron dev mode |
| `pnpm electron:build` | Build Electron app |
| `pnpm cli` | Run CLI tool |

## 🎯 System Requirements

### Minimum
- **CPU**: Dual-core processor (Intel/AMD)
- **RAM**: 4GB
- **GPU**: Intel HD Graphics (optional)
- **Storage**: 2GB free space + model storage

### Recommended
- **CPU**: Quad-core processor or better
- **RAM**: 8GB or more
- **GPU**: NVIDIA GPU with CUDA support (optional)
- **Storage**: SSD with 10GB+ free space

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [Contributing Guide](docs/contributing.md)
- [AirLLM Setup](docs/airllm-setup.md)
- [Model Management](docs/model-management.md)
- [Extension Development](docs/extension-development.md)
- [Performance Tuning](docs/performance-tuning.md)
- [Offline Usage](docs/offline-usage.md)
- [Security Best Practices](docs/security.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install hooks
pnpm prepare

# Run type checking
pnpm typecheck

# Run tests
pnpm test
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [AirLLM](https://github.com/mit-han-lab/airllm) - Efficient LLM inference
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - LLM inference in C++
- [Monaco Editor](https://microsoft.github.io/monaco-editor/) - Code editor
- [Electron](https://www.electronjs.org/) - Cross-platform desktop apps
- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) - Parsing library

---

Built with ❤️ by the Codex IDE Team
