"""
System Verification Script.

Run this script to perform a "smoke test" on all backend components.
It verifies that:
1. All modules can be imported.
2. Integration factories are wiring up correctly.
3. The Voice Agent logic executes without errors.
4. The Crawler class instantiates (though actual crawling requires internet/browser).

Usage:
    python verify_setup.py
"""

import asyncio
import sys
import os

# Add current dir to path
sys.path.append(os.getcwd())

from app.components.integrations import TicketAdapterFactory
from app.components.voice import VoiceSchedulerAgent
from app.services import AnalyticsService

def test_integrations():
    print("Testing Integrations...")
    providers = ["HubSpot", "Jira", "Zendesk", "Salesforce"]
    for p in providers:
        adapter = TicketAdapterFactory.get_adapter(p)
        ticket = adapter.create_ticket("Test Title", "Test Desc", "High")
        print(f"  [OK] {p}: Created ticket {ticket['id']}")

async def test_crawler_import():
    print("Testing Crawler Import...")
    from app.components.crawler import CrawlerService
    c = CrawlerService()
    print("  [OK] CrawlerService instantiated")

async def test_voice():
    print("Testing Voice Agent...")
    agent = VoiceSchedulerAgent()
    res = await agent.process_lead({"id": "TEST-1", "phone": "123"})
    print(f"  [OK] Voice Agent Plan: {res['scheduled_time']}")

async def main():
    try:
        test_integrations()
        await test_crawler_import()
        await test_voice()
        print("\nAll systems operational.")
    except Exception as e:
        print(f"\n[ERROR] Verification Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
