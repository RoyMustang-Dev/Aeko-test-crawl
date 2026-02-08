"""
Concrete Ticket Provider Implementations.

This module contains the specific implementations for various third-party
ticketing systems (HubSpot, Jira, Zendesk, Salesforce). Each class implements
the `BaseTicketAdapter` interface.

NOTE: For demonstration purposes, actual API calls are mocked using standard
libraries like `uuid` and `random` to simulate external system responses.
"""

import random
import uuid
from typing import Dict, Any
from .base import BaseTicketAdapter

class HubSpotAdapter(BaseTicketAdapter):
    """Adapter for HubSpot Service Hub."""
    
    def create_ticket(self, title: str, description: str, priority: str) -> Dict[str, Any]:
        """
        Simulates creating a ticket in HubSpot.
        """
        # Mocking a HubSpot Ticket ID (usually numeric)
        ticket_id = f"HS-{random.randint(1000, 9999)}"
        
        return {
            "provider": "HubSpot",
            "id": ticket_id,
            "status": "OPEN",
            # HubSpot internal priority values are often uppercase (LOW, MEDIUM, HIGH)
            "priority": priority.upper(),
            # Constructing a valid-looking URL for the user to visit
            "link": f"https://app.hubspot.com/tickets/{ticket_id}"
        }

    def get_status(self, external_id: str) -> str:
        return "OPEN"

class JiraAdapter(BaseTicketAdapter):
    """Adapter for Atlassian Jira."""

    def create_ticket(self, title: str, description: str, priority: str) -> Dict[str, Any]:
        """
        Simulates creating a ticket in Jira.
        """
        # Mocking a Jira Project Key format (e.g., PROJ-123)
        ticket_id = f"PROJ-{random.randint(100, 999)}"
        
        return {
            "provider": "Jira",
            "id": ticket_id,
            "status": "TO DO", # Jira uses kanban states like 'TO DO'
            "priority": priority,
            "link": f"https://jira.atlassian.com/browse/{ticket_id}"
        }

    def get_status(self, external_id: str) -> str:
        return "OPEN"

class ZendeskAdapter(BaseTicketAdapter):
    """Adapter for Zendesk Support."""

    def create_ticket(self, title: str, description: str, priority: str) -> Dict[str, Any]:
        """
        Simulates creating a ticket in Zendesk.
        """
        # Zendesk IDs are typically long integers
        ticket_id = str(random.randint(10000, 99999))
        
        return {
            "provider": "Zendesk",
            "id": ticket_id,
            "status": "new", # Zendesk default status is lowercase 'new'
            "priority": priority.lower(), # Zendesk expects lowercase priority logic
            "link": f"https://support.zendesk.com/tickets/{ticket_id}"
        }

    def get_status(self, external_id: str) -> str:
        return "OPEN"

class SalesforceAdapter(BaseTicketAdapter):
    """Adapter for Salesforce Service Cloud."""

    def create_ticket(self, title: str, description: str, priority: str) -> Dict[str, Any]:
        """
        Simulates creating a Case in Salesforce.
        """
        # Salesforce IDs are alphanumeric strings (15 or 18 chars)
        # We mock this using part of a UUID
        ticket_id = "500" + str(uuid.uuid4())[:15]
        
        return {
            "provider": "Salesforce",
            "id": ticket_id,
            "status": "New",
            "priority": priority,
            "link": f"https://salesforce.com/{ticket_id}"
        }

    def get_status(self, external_id: str) -> str:
        return "OPEN"
