# 🎵 CabaBot - Enterprise-Grade Discord Music Bot

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Discord](https://img.shields.io/badge/Discord-API-5865F2.svg)](https://discord.com/developers/docs)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Async](https://img.shields.io/badge/Async-await-brightgreen.svg)](https://docs.python.org/3/library/asyncio.html)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com/)

> **👨‍💻 Developed by Gabriel Penha (Gabaoun)**
>
> **CabaBot** is a high-performance, asynchronous Discord music bot designed to demonstrate expertise in modern software engineering, real-time audio processing, and scalable architecture. It features seamless API integration, robust error handling, and a reactive user interface.

## 💼 Tech Stack & Architecture

### 🎯 Core Technologies
| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Python 3.13+ | Modern syntax with strict type hinting |
| **Framework** | discord.py | Asynchronous API Gateway interaction |
| **Concurrency** | asyncio | Non-blocking I/O for high-performance operations |
| **Audio Engine** | FFmpeg + yt-dlp | Real-time adaptive audio streaming & transcoding |
| **Integrations** | Spotify API (Spotipy) | Cross-platform track resolution & metadata fetching |
| **Frontend/UI** | discord.ui | Reactive components (Buttons, Modals, Select Menus) |
| **DevOps** | Docker + Compose | Containerized, production-ready deployment |
| **QA & Type Safety** | mypy, pytest | Static analysis and automated testing |

### 🏗️ Design Patterns & Engineering Practices
This project implements several key software design patterns to ensure maintainability and scalability:

- **Observer Pattern**: Utilized for an event-driven architecture, handling Discord voice state updates and user interactions reactively.
- **Strategy Pattern**: Decouples audio source handling, allowing seamless switching between providers (YouTube, Spotify) without altering core logic.
- **Factory Pattern**: Dynamically manages per-server player instances, ensuring isolated states for multiple concurrent guilds.
- **Command Pattern**: Encapsulates user requests as objects, enabling features like undo/redo for queue operations and transactional command execution.
- **Singleton**: Manages shared resources such as database connections and the global voice client manager to prevent race conditions.

## 🚀 Enterprise Features

### 🎵 Audio & Streaming
- **High-Fidelity Streaming**: Real-time audio processing with `loudnorm` normalization for consistent volume levels across tracks.
- **Adaptive Quality**: Automatically selects the best available audio format to balance quality and bandwidth.
- **Cross-Platform Compatibility**: Intelligent resolution of Spotify links (tracks, albums, playlists) to streamable YouTube sources.

### 🎮 User Experience (UX)
- **Interactive Dashboard**: Rich embed interfaces with persistent controls (Play, Pause, Skip, Shuffle) using Discord's UI Kit.
- **Smart Queue Management**: Per-server isolated playlists with support for reordering, removal, and loop modes.
- **Asynchronous Timers**: Non-blocking scheduling system for user reminders and automated tasks.

### 🛡️ Reliability & Security
- **Zero-Downtime Architecture**: Designed to handle API rate limits and connection drops gracefully with auto-reconnection logic.
- **Input Sanitization**: Rigorous validation of user inputs to prevent command injection and ensure system stability.
- **Resource Optimization**: Efficient memory management for 24/7 operation, utilizing `asyncio` to handle thousands of concurrent events.

## 🚀 Getting Started

### Option 1: Docker (Recommended)
The cleanest way to run the application, ensuring an isolated and consistent environment.

1.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    TOKEN=your_discord_bot_token
    # Optional: For Spotify support
    SPOTIPY_CLIENT_ID=your_client_id
    SPOTIPY_CLIENT_SECRET=your_client_secret
    ```
2.  **Deploy**:
    ```bash
    docker-compose up -d
    ```

### Option 2: Local Development
For contributors or those wishing to debug the source code directly.

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd CabaBot
    ```

2.  **Install Dependencies**
    Requires FFmpeg installed on your system path.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Bot**
    ```bash
    python CabaBot.py
    ```

---
*Developed for portfolio and educational purposes.*
