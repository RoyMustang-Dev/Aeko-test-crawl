# 🚀 Aeko Backend Integrations Demo

Welcome to the **Aeko integrations showcase**. This repository demonstrates a modern, high-performance backend architecture capable of handling complex tasks like **parallel web crawling**, **unified ticketing**, and **autonomous voice agents**.

It is designed to be a reference implementation for building scalable, async-first Python applications using **Streamlit**, **Playwright**, and **SQLite**.

---

## 🌟 Key Features & Rationale

We didn't just build features; we built them to solve specific scalability and usability problems.

### 1. High-Performance Knowledge Crawler

- **Feature:** Crawls websites efficiently using a "Producer-Consumer" architecture.
- **Why?** Standard linear crawlers are too slow. We use **Asyncio** and **Playwright** to run multiple browser tabs (workers) in parallel.
- **Key Tech:**
  - **Smart Queue:** URLs are prioritized by entropy and depth, not just FIFO.
  - **Non-Blocking I/O:** A dedicated "Database Writer" task saves data to SQLite in the background, so the crawler never stops to wait for disk writes.
  - **Anti-Blocking:** Checks `robots.txt` and simulates human browsing to avoid bans.

### 2. Unified Ticketing System

- **Feature:** A single API to create tickets in HubSpot, Jira, Zendesk, or Salesforce.
- **Why?** Businesses use different tools. We used the **Adapter Design Pattern** to create a standard interface (`create_ticket`). You write code once, and it works for any provider.
- **Key Tech:** Abstract Base Classes (ABC), Factory Pattern.

### 3. Proactive Voice Agent

- **Feature:** An autonomous agent that "plans" a conversation and schedules calls.
- **Why?** Static forms are outdated. This authenticates the concept of an AI that proactively reaches out to customers to resolve issues.
- **Key Tech:** Simulation of LLM "reasoning" steps and async state management.

### 4. Real-Time Analytics

- **Feature:** centralized tracking of every action (ticket created, crawl finished).
- **Why?** Observability is critical. We implemented a **Singleton** analytics service that aggregates data across the entire user session.

---

## 📂 Project Structure

Here is a roadmap of the files in this repository.

```text
aeko-project/
├── app/
│   ├── components/
│   │   ├── crawler/
│   │   │   ├── service.py       # 🧠 CORE: The advanced async crawler logic (Playwright + Queues)
│   │   ├── integrations/
│   │   │   ├── base.py          # 📐 Interface: Defines how ALL ticket adapters must behave
│   │   │   ├── factory.py       # 🏭 Factory: Creates the right adapter (HubSpot/Jira) on demand
│   │   │   ├── providers.py     # 🔌 Adapters: Concrete implementations for each provider
│   │   ├── voice/
│   │   │   ├── agent.py         # 🗣️ Agent: Handles call planning and simulation
│   ├── services/
│   │   ├── analytics.py         # 📊 Singleton service for tracking app stats
│   ├── database.py              # 💾 SQLite persistence layer (WAL mode enabled)
├── dashboard.py                 # 🖥️ UI: Main Streamlit application entry point
├── verify_setup.py              # ✅ Script to test if your environment is set up correctly
├── requirements.txt             # 📦 List of python dependencies
├── setup_env.sh                 # 🛠️ Helper script to create virtualenv
└── README.md                    # 📖 You are here
```

---

## 🛠️ Setup Guide (For Beginners)

Follow these steps to get the project running on your local machine.

### Prerequisites

- **Python 3.8+** installed.
- **Google Chrome** or Chromium installed (automated by Playwright).

### Step 1: Clone & Configure Environment

Open your terminal and run:

```bash
# 1. Create a virtual environment (keeps dependencies clean)
python3 -m venv venv

# 2. Activate the environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 2: Install Dependencies

Install all required libraries:

```bash
pip install -r requirements.txt
```

### Step 3: Install Browsers

Playwright needs its own browser binaries to run the crawler:

```bash
playwright install chromium
```

### Step 4: Verify Installation

Run our self-check script to make sure everything is working:

```bash
python verify_setup.py
```

_If you see "All systems operational", you are ready!_

---

## 🖥️ How to Run

Start the dashboard user interface:

```bash
streamlit run dashboard.py
```

This will automatically open **http://localhost:8501** in your web browser.

### Usage Instructions

#### 1. Knowledge Crawler Tab

- Enter a URL (e.g., `https://en.wikipedia.org/wiki/Artificial_intelligence`).
- **Browser Simulation Mode**: Check this to see the browser open and scroll (fun to watch!).
- **Auto-Crawl Links**: Check this to crawl deeper than just the first page.
- Click **Start Crawling** and watch the logs.

#### 2. Ticket Integrations Tab

- Fill out the ticket form (Title, Description).
- Select a provider (e.g., Jira).
- Click **Create Ticket**. You'll see a simulated success response and a mock link.

#### 3. Voice Agent Tab

- Enter a fake Ticket ID and Phone Number.
- Click **Trigger Agent Call**.
- The agent will "think", initiate a call, and return a transcript of the conversation.

---

## 📝 Developer Notes

- **Database**: Data is stored in `crawler_data.db`. It uses **WAL (Write-Ahead Logging)** mode for performance. You can open this file with any SQLite viewer.
- **Asyncio**: The crawler relies heavily on Python's `asyncio`. If you modify `crawler/service.py`, remember to use `await` for any I/O operations.
