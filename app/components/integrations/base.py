"""
Unified Ticketing Interface.

This module defines the abstract base class that all ticketing backend adapters
must implement. This enforces a consistent API (create_ticket, get_status)
regardless of whether the underlying provider is HubSpot, Jira, etc.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTicketAdapter(ABC):
    """
    Abstract Base Class for Ticket System Adapters.

    This class enforces the Adapter Design Pattern, ensuring all subclasses
    expose the same methods to the main application.
    """

    @abstractmethod
    def create_ticket(self, title: str, description: str, priority: str) -> Dict[str, Any]:
        """
        Creates a new ticket in the external system.

        Args:
            title (str): The subject or summary of the ticket.
            description (str): Detailed explanation of the issue.
            priority (str): Urgency level (e.g., 'High', 'Medium', 'Low').

        Returns:
            Dict[str, Any]: A standardized dictionary containing at least:
                - id (str): The external system's unique ticket ID.
                - link (str): A direct URL to view the ticket.
                - status (str): The initial status.
        """
        pass

    @abstractmethod
    def get_status(self, external_id: str) -> str:
        """
        Retrieves the current status of a specific ticket.

        Args:
            external_id (str): The ID of the ticket to check.

        Returns:
            str: A normalized status string (e.g., "OPEN", "CLOSED").
        """
        pass
