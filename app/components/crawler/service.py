"""
Crawler Service Component.

Refactored for High Performance:

FIXES APPLIED:
1. URL-agnostic Smart Selection using entropy + similarity.
2. Parallel DB Writer Queue (OPTION A).
3. Thread-safe visited set via asyncio.Lock.
4. Zero-lag persistence (workers never touch SQLite).
5. Safe worker shutdown (no cancellation).
"""

import asyncio
import os
import json
import urllib.robotparser
import requests
import uuid
import math
from urllib.parse import urlparse, urljoin
from datetime import datetime
from playwright.async_api import async_playwright, Page, BrowserContext
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from app.database import init_db, insert_page_async, get_all_pages, enable_wal

class CrawlerService:

    def __init__(self):
        init_db()
        enable_wal()

    # ---------------- SMART URL SCORING (NO KEYWORDS) ---------------- #

    def _url_entropy(self, url: str) -> float:
        probs = [url.count(c)/len(url) for c in set(url)]
        return -sum(p * math.log2(p) for p in probs)

    def _similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    def _get_best_links(self, links: list, visited: set, limit: int = 5) -> list:
        """
        Truly generic smart selection:
        • URL entropy
        • path length
        • depth
        • duplicate similarity
        """

        scored = []

        for link in links:
            u = urlparse(link)
            path = u.path

            depth = len(list(filter(None, path.split("/"))))
            entropy = self._url_entropy(link)
            plen = len(path)

            dup_penalty = 0
            for v in visited:
                if self._similarity(link, v) > 0.85:
                    dup_penalty -= 5

            score = entropy + (2 <= depth <= 4) * 2 + (20 < plen < 120) * 2 + dup_penalty
            scored.append((score, link))

        scored.sort(reverse=True)
        return [x[1] for x in scored[:limit]]

    # ---------------- ROBOTS ---------------- #

    def _get_robots_parser(self, url):
        parsed = urlparse(url)
        robots = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        try:
            r = requests.get(robots, timeout=5)
            rp.parse(r.text.splitlines())
        except:
            rp.allow_all = True
        return rp

    def is_allowed(self, url, rp):
        try:
            return rp.can_fetch("*", url)
        except:
            return True

    # ---------------- ASYNC DB WRITER ---------------- #

    async def _db_writer(self, queue):
        """
        Dedicated persistence coroutine.
        Workers push records here.
        This completely removes SQLite from crawler critical path.
        """
        while True:
            item = await queue.get()
            if item is None:
                break
            insert_page_async(*item)
            queue.task_done()

    # ---------------- WORKER ---------------- #

    async def _worker(self, wid, queue, context, session_id, rp,
                      visited, visited_lock, db_queue, simulate):

        page = await context.new_page()

        while True:
            item = await queue.get()
            if item is None:
                queue.task_done()
                break

            url, depth, max_depth = item

            async with visited_lock:
                if url in visited:
                    queue.task_done()
                    continue
                visited.add(url)

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                title = await page.title()
                content = await page.evaluate("document.body.innerText")

                # Async persistence (non-blocking)
                await db_queue.put((session_id, url, title, content, depth, "success"))

                if depth < max_depth:
                    soup = BeautifulSoup(await page.content(), "html.parser")
                    discovered = []

                    for a in soup.find_all("a", href=True):
                        full = urljoin(url, a["href"])
                        if full.startswith("http") and urlparse(full).netloc == urlparse(url).netloc:
                            if self.is_allowed(full, rp):
                                discovered.append(full)

                    if depth < 2:
                        targets = list(set(discovered))[:50]
                    else:
                        async with visited_lock:
                            targets = self._get_best_links(list(set(discovered)), visited)

                    for t in targets:
                        await queue.put((t, depth + 1, max_depth))

            except Exception as e:
                await db_queue.put((session_id, url, "Error", str(e), depth, "failed"))

            queue.task_done()

        await page.close()

    # ---------------- ENTRY ---------------- #

    async def crawl_url(self, url: str, save_folder: str = None, simulate: bool = False, recursive: bool = False, max_depth: int = 1) -> dict:
        """
        Orchestrates the crawling process using a pool of worker tasks and a dedicated database writer.

        Architecture:
        - Uses a Producer-Consumer pattern where workers (Producer) fetch pages and push data to queues.
        - `queue`: Holds URLs to be crawled.
        - `db_queue`: Holds extracted data to be written to SQLite.
        - `_db_writer`: A dedicated consumer task that writes to SQLite, ensuring the UI/crawler never blocks on I/O.

        Args:
            url (str): The seed URL to start crawling from.
            save_folder (str, optional): Path to save JSON/TXT reports. Defaults to None.
            simulate (bool): If True, runs headful browser to visualize the process. Defaults to False.
            recursive (bool): If True, follows links within the same domain. Defaults to False.
            max_depth (int): Maximum depth to traverse if recursive is True.

        Returns:
            dict: A summary report containing status, stats, and a preview of extracted content.
        """
        
        start_time = datetime.now()
        session_id = str(uuid.uuid4())

        visited = set()
        visited_lock = asyncio.Lock()

        queue = asyncio.Queue()
        db_queue = asyncio.Queue()

        rp = self._get_robots_parser(url)
        if not self.is_allowed(url, rp):
            return {"status": "blocked"}

        queue.put_nowait((url, 0, max_depth if recursive else 0))

        async with async_playwright() as p:

            browser = await p.chromium.launch(headless=not simulate)

            NUM = 6
            contexts = [await browser.new_context() for _ in range(NUM)]

            # Start DB writer
            db_task = asyncio.create_task(self._db_writer(db_queue))

            workers = [
                asyncio.create_task(
                    self._worker(i, queue, contexts[i], session_id,
                                 rp, visited, visited_lock, db_queue, simulate)
                )
                for i in range(NUM)
            ]

            await queue.join()

            # graceful shutdown
            for _ in workers:
                await queue.put(None)

            await asyncio.gather(*workers)

            await db_queue.join()
            await db_queue.put(None)
            await db_task

            rows = get_all_pages(session_id)

            full = ""
            for r in rows:
                full += f"\n\n== {r['title']} ==\n{r['content']}"

            # Calculate metrics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Prepare data
            rows_data = [dict(r) for r in rows] # Convert sqlite3.Row to dict
            
            # File Saving Logic
            saved_files = []
            if save_folder:
                if not os.path.exists(save_folder):
                    os.makedirs(save_folder)
                
                # 1. Save Full Report (JSON)
                report_path = os.path.join(save_folder, "crawl_report.json")
                report_data = {
                    "url": url,
                    "session_id": session_id,
                    "timestamp": start_time.isoformat(),
                    "duration_seconds": duration,
                    "pages_crawled": len(rows),
                    "pages": rows_data
                }
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(report_data, f, indent=2)
                saved_files.append(report_path)

                # 2. Save Content (TXT)
                content_path = os.path.join(save_folder, "crawled_content.txt")
                with open(content_path, "w", encoding="utf-8") as f:
                    f.write(full)
                saved_files.append(content_path)

            return {
                "url": url,
                "status": "success",
                "session_id": session_id,
                "pages_crawled": len(rows),
                "full_text": full,
                "content_preview": full[:500] + "...",
                "links": {"allowed": [], "blocked": []},
                "duration": round(duration, 2),
                "crawl_only_duration": round(duration, 2),
                "saved_files": saved_files,
                "database_records": rows_data
            }
