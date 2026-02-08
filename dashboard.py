"""
Streamlit Dashboard for Aeko Integrations.

This application serves as the user interface to demonstrate the backend capabilities
of the Aeko platform. It connects to the Crawler, Ticketing, and Voice agents
and provides interactive controls for verifying their functionality.

Usage:
    streamlit run dashboard.py
"""

import streamlit as st
import asyncio
import os
import pandas as pd
# Import our custom backend components
from app.components.crawler import CrawlerService
from app.components.integrations import TicketAdapterFactory
from app.components.voice import VoiceSchedulerAgent
from app.services import AnalyticsService

# Configure the Streamlit page layout
st.set_page_config(page_title="Aeko Backend Demo", layout="wide")
st.title("Aeko Integrations Dashboard")

# Initialize Services
# -------------------
# We use Streamlit's `session_state` to maintain singleton instances of our services across reruns.
# This prevents re-initializing connections or losing state (like the voice agent's history)
# when the user interacts with buttons.

# Always re-init crawler to pick up code changes during development (Hot Reload friendly)
st.session_state.crawler_service = CrawlerService()

# Voice Agent needs persistence to remember call history
if 'voice_agent' not in st.session_state:
    st.session_state.voice_agent = VoiceSchedulerAgent()

# Analytics needs persistence to aggregate events across the session
if 'analytics' not in st.session_state:
    st.session_state.analytics = AnalyticsService()

# Sidebar Navigation
tab = st.sidebar.radio("Navigation", ["Knowledge Crawler", "Ticket Integrations", "Voice Agent", "Analytics"])

# --- TAB 1: KNOWLEDGE CRAWLER ---
if tab == "Knowledge Crawler":
    st.header("1. Parallel Knowledge Crawler")
    st.markdown("Crawls websites using Playwright while allowing parallel file uploads.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Web Crawler")
        
    with col1:
        st.subheader("Web Crawler")
        
        # User inputs
        # Use simple key mechanism to allow 'rerun' without full refresh logic issues
        current_url = st.text_input("Enter URL", "https://en.wikipedia.org/wiki/Artificial_intelligence", key="url_input")
        save_dir = st.text_input("Output Folder", "crawled_data", key="folder_input")
        
        # New Controls
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            enable_simulation = st.checkbox("Browser Simulation Mode", help="Opens the browser window visibly and scrolls.")
        with col_ctrl2:
            enable_recursive = st.checkbox("Auto-Crawl Links", help="Recursively crawls internal links.")
            
        # Recursive Depth Control (Conditional)
        max_depth = 1
        if enable_recursive:
            max_depth = st.slider("Crawl Depth (Levels)", min_value=1, max_value=3, value=1, help="1=Children, 2=Grandchildren. Higher depth = longer crawl time.")

        if st.button("Start Crawling", key="crawl_btn"):
            st.info(f"Starting crawl for {current_url}...")
            
            # Dynamic Spinner Message
            msg = "Crawling..."
            if enable_simulation: msg += " (Check opened browser window!)"
            if enable_recursive: msg += f" (Depth: {max_depth} - Reading child pages...)"

            with st.spinner(msg):
                try:
                    abs_save_path = os.path.abspath(save_dir)
                    
                    # Call backend with new arguments
                    results = asyncio.run(st.session_state.crawler_service.crawl_url(
                        url=current_url, 
                        save_folder=abs_save_path,
                        simulate=enable_simulation,
                        recursive=enable_recursive,
                        max_depth=max_depth
                    ))
                    
                    if results.get("status") == "success":
                        duration = results.get("duration", 0.0)
                        st.success(f"Crawl Completed & Saved! (Time Taken: {duration}s)")
                        
                        if enable_recursive:
                            st.info(f"Recursive Crawl: Processed {results.get('pages_crawled', 1)} pages (Depth {max_depth}).")
                        
                        # A. CRAWLABLE VS BLOCKED CONTENT (List View)
                        st.subheader("Link Analysis (Robots.txt)")
                        
                        with st.expander("View Crawlable vs. Blocked Links", expanded=True):
                            l_col1, l_col2 = st.columns(2)
                            
                            allowed_links = results.get("links", {}).get("allowed", [])
                            blocked_links = results.get("links", {}).get("blocked", [])
                            
                            with l_col1:
                                st.markdown(f"**✅ Crawlable Links ({len(allowed_links)})**")
                                st.write(allowed_links[:20]) # Limit display
                                if len(allowed_links) > 20: st.caption("...and more")
                                
                            with l_col2:
                                st.markdown(f"**🚫 Blocked by Robots.txt ({len(blocked_links)})**")
                                if blocked_links:
                                    st.error(f"Found {len(blocked_links)} blocked links.")
                                    st.write(blocked_links)
                                else:
                                    st.success("No blocked links found.")

                        # B. SAVED FILES POPUP
                        st.subheader("📁 Saved Files")
                        for fpath in results.get("saved_files", []):
                            st.code(fpath, language="text")
                            
                        # C. CONTENT PREVIEW
                        st.subheader("Content Preview")
                        st.text_area("Extracted Text", results.get("content_preview", ""), height=200)

                        # D. DATABASE RECORDS
                        if "database_records" in results:
                            st.subheader("Database Records (SQLite)")
                            st.info(f"Session ID: {results.get('session_id')}")
                            df = pd.DataFrame(results["database_records"])
                            if not df.empty:
                                st.dataframe(
                                    df[["id", "url", "title", "depth", "status", "timestamp"]],
                                    use_container_width=True,
                                    hide_index=True
                                )
                            else:
                                st.warning("No records found in database.")

                    elif results.get("status") == "blocked":
                        st.warning("⛔ Crawl Blocked by Robots.txt")
                        st.error(f"Reason: {results.get('error')}")

                    else:
                        st.error(f"Crawl Failed: {results.get('error')}")
                        
                except Exception as e:
                    st.error(f"Execution Error: {e}")

    with col2:
        st.subheader("Parallel Upload Simulation")
        uploaded_file = st.file_uploader("Upload Knowledge File (Simulated)")
        if uploaded_file:
            st.info("File received. Simulating processing...")
            # Simulate parallel processing
            result = asyncio.run(st.session_state.crawler_service.simulate_parallel_upload(uploaded_file.name))
            st.success(f"Processed {result['filename']} at {result['timestamp']}")

# --- TAB 2: TICKET INTEGRATIONS ---
elif tab == "Ticket Integrations":
    st.header("2. Unified Ticketing Integrations")
    st.markdown("Create tickets across multiple providers using a unified adapter interface.")
    
    with st.form("ticket_form"):
        title = st.text_input("Ticket Title", "Issue with Login")
        desc = st.text_area("Description", "User cannot login via Google OAuth.")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        provider = st.selectbox("Select Provider", ["HubSpot", "Jira", "Zendesk", "Salesforce"])
        
        submitted = st.form_submit_button("Create Ticket")
        
        if submitted:
            try:
                adapter = TicketAdapterFactory.get_adapter(provider)
                ticket = adapter.create_ticket(title, desc, priority)
                
                # Log to Analytics
                st.session_state.analytics.log_event("TICKET_CREATED", provider, ticket)
                
                st.success(f"Ticket Created in {provider}!")
                st.json(ticket)
                
                # Mock Link
                st.markdown(f"[View in {provider}]({ticket['link']})")
                
            except Exception as e:
                st.error(f"Error: {e}")

# --- TAB 3: VOICE AGENT ---
elif tab == "Voice Agent":
    st.header("3. Proactive Voice Agent")
    st.markdown("Autonomous calling agent that schedules follow-ups based on ticket status.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        t_id = st.text_input("Ticket ID Reference", "HS-1234")
        phone = st.text_input("Customer Phone", "555-0199")
        if st.button("Trigger Agent Call"):
            with st.spinner("Agent is planning and initiating call..."):
                ticket_data = {"id": t_id, "phone": phone}
                
                # Run async agent
                try:
                    result = asyncio.run(st.session_state.voice_agent.process_lead(ticket_data))
                    st.session_state.last_call = result
                    st.success("Call Completed!")
                except Exception as e:
                    st.error(f"Call Failed: {e}")

    with col2:
        if 'last_call' in st.session_state:
            st.subheader("Call Summary")
            call = st.session_state.last_call
            
            st.info(f"**Call ID:** {call['call_id']}")
            st.text_area("Transcript", call['transcript'], height=150)
            
            st.success(f"Action Taken: Scheduled for {call['scheduled_time']}")
            
            # Log this event too
            st.session_state.analytics.log_event("VOICE_CALL_COMPLETED", "Twilio (Mock)", call)

# --- TAB 4: ANALYTICS ---
elif tab == "Analytics":
    st.header("4. System Analytics")
    
    stats = st.session_state.analytics.get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Tickets Created", stats["total_tickets"])
    
    st.subheader("Tickets by Provider")
    if stats["by_provider"]:
        st.bar_chart(pd.Series(stats["by_provider"]))
    else:
        st.info("No tickets created yet.")
        
    st.subheader("Recent Event Log")
    if stats["recent_events"]:
        st.table(pd.DataFrame(stats["recent_events"]))
    else:
        st.info("No events logged.")
