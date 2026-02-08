"""
Centralized Analytics Service.

This module provides a simple event tracking system. In a production environment,
this would likely interface with a data warehouse (Snowflake/BigQuery) or an
observability tool (Datadog/PostHog). Here, it uses an in-memory list.
"""

from collections import defaultdict
from datetime import datetime

class AnalyticsService:
    """
    Singleton class for logging and retrieving application events.
    
    Uses the Singleton pattern to ensure that all parts of the application
    write to the same event log during the session runtime.
    """
    
    _instance = None
    
    def __new__(cls):
        """Standard pythonic way to implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(AnalyticsService, cls).__new__(cls)
            cls._instance.events = []
        return cls._instance

    def log_event(self, event_type: str, provider: str, details: dict = None):
        """
        Record a new event.

        Args:
            event_type (str): Category of event (e.g., 'TICKET_CREATED').
            provider (str): Source system (e.g., 'HubSpot').
            details (dict, optional): Extra payload data.
        """
        event = {
            "timestamp": datetime.now(),
            "type": event_type,
            "provider": provider,
            "details": details or {}
        }
        self.events.append(event)

    def get_stats(self) -> dict:
        """
        Computes aggregate statistics from the raw event log.
        
        Returns:
            dict: Structured stats including totals and recent history.
        """
        stats = {
            "total_tickets": 0,
            "by_provider": defaultdict(int),
            "recent_events": []
        }
        
        for event in self.events:
            # Aggregate Ticket Creation events
            if event["type"] == "TICKET_CREATED":
                stats["total_tickets"] += 1
                stats["by_provider"][event["provider"]] += 1
        
        # Convert defaultdict to standard dict for clean serialization
        stats["by_provider"] = dict(stats["by_provider"])
        # Return only the last 10 events for UI display
        stats["recent_events"] = self.events[-10:] 
        
        return stats
