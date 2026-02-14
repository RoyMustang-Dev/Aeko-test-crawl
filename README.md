# 🚀 Aeko Intelligent Crawler Integration

This repository contains the **Aeko Intelligent Crawler**, an enterprise-grade web crawling module designed for backward integration into B2B platforms. It functions as a plug-and-play microservice for autonomous knowledge extraction.

---

## 🌟 Integration Readiness

**Status:** Ready for Commercial Integration.
**Architecture:** Asyncio-based "Producer-Consumer" pattern with SLA compliance features.

### Commercial-Grade Capabilities

1.  **Zero-Blocking Architecture**: Runs asynchronously on a separate event loop, ensuring the parent application's main thread is never blocked.
2.  **Resource Efficiency**: Blocks ~60% of unnecessary bandwidth (images, fonts, media) via request interception.
3.  **Governance & Compliance**: Strict `robots.txt` adherence and an instant "Stop Switch" for liability control.
4.  **Data Hygiene**: Delivers "clean" text by automatically stripping HTML headers, footers, and navigation.

---

## 🌟 Technical Specifications & Features

### 1. High-Throughput Crawler Engine

_Core Logic: `app/components/crawler/service.py`_

| Feature                 | Description                                                        | Implementation Detail                              |
| :---------------------- | :----------------------------------------------------------------- | :------------------------------------------------- |
| **Parallel Workers**    | Runs **15 concurrent headless browsers** for maximum speed.        | `service.py`: `NUM = 15` (Line 290)                |
| **Instant Stop**        | Race-condition based cancellation for immediate (<3s) halting.     | `service.py`: `asyncio.wait(..., FIRST_COMPLETED)` |
| **Resource Blocking**   | Intercepts and aborts requests for images, fonts, CSS, & ads.      | `service.py`: `route.abort()` (Line 163)           |
| **Smart Deduplication** | Removes `header`, `footer`, `nav`, `aside` tags before extraction. | `service.py`: `_clean_content()` (Line 130)        |
| **URL Normalization**   | Auto-prefixes `https://` if missing.                               | `service.py`: `starts_with("http")`                |
| **Canonical Tracking**  | Tracks final URL after redirects (e.g., booking.com/params).       | `service.py`: `page.url` (Line 198)                |
| **Stealth Mode**        | Sets user-agent and handles basic CAPTCHA clicks.                  | `service.py`: `_handle_captcha()` (Line 117)       |

### 2. Configurable Crawl Modes

_Control Interface: `dashboard.py`_

- **Auto-Crawl (Recursive)**:
  - **Functionality**: Automatically discovers and follows links within the same domain.
  - **Control**: Set `Max Depth` (1-3) to control how "deep" the crawler goes.
  - **Logic**: Uses robust scoring (entropy + path length) to prioritize "content-rich" links over "administrative" links.

- **Browser Simulation (Headful Mode)**:
  - **Functionality**: Opens a visible browser window to visualize the crawling process.
  - **Use Case**: Debugging anti-bot measures or visual verification.
  - **Performance**: Slower than default (Headless) mode but useful for demos.

- **Output Management**:
  - **Functionality**: Saves all crawled data to a specified local directory.
  - **Structure**: Creates `JSON` (metadata) and `TXT` (clean content) files for every page.

---

## 📂 Module Structure

```text
aeko-project/
├── app/
│   ├── components/
│   │   ├── crawler/
│   │   │   ├── service.py       # 🧠 CORE PRODUCT: The integration-ready crawler module
│   │   ├── integrations/        # 🔌 Adapters for external services
│   ├── services/
│   │   ├── analytics.py         # 📊 Telemetry & Usage Tracking
│   ├── database.py              # 💾 Persistence Layer (WAL mode enabled)
├── dashboard.py                 # 🖥️ Admin UI: For testing and monitoring the module
├── requirements.txt             # 📦 Dependency Manifest
└── README.md                    # 📖 Integration Documentation
```

---

## 🛠️ Integration Guide

### Prerequisites

1. **Python 3.8+** environment.
2. **Xcode Command Line Tools** (Mac Only):
   - Run `xcode-select --install` to ensure compiler compatibility.
3. **Watchdog** (Optional):
   - Run `pip install watchdog` for hot-reload during development.

### Setup

```bash
# 1. Create & Activate Virtual Environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts/activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Install Playwright Browsers
playwright install chromium

# 4. Launch Module Interface
streamlit run dashboard.py
```

---

## ❓ Technical FAQ

**Q: Is this ready to be used as a backend module?**
A: **Yes.** The core `CrawlerService` class is self-contained and stateless (besides the database). It allows seamless integration into larger Python architectures (FastAPI, Django).

**Q: Does it handle scaling?**
A: **Yes.** Utilizing `asyncio`, the module maximizes single-node throughput (15+ concurrent pages). Its stateless design supports multi-node scaling behind a load balancer.

**Q: How is data consistency handled?**
A: SQLite **WAL (Write-Ahead Logging)** mode (`app/database.py`) is enabled by default, ensuring high-speed writes without blocking concurrent reads from the parent application.
