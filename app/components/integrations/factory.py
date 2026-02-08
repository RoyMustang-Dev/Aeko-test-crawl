"""
Ticket Adapter Factory.

This module implements the Factory Method Design Pattern. It allows the rest of the
application to request a ticket adapter by string name (e.g., "HubSpot") without
needing to import or know about the specific concrete classes.
"""

from .base import BaseTicketAdapter
from .providers import HubSpotAdapter, JiraAdapter, ZendeskAdapter, SalesforceAdapter

class TicketAdapterFactory:
    """
    Factory class for creating TicketAdapter instances.
    """

    @staticmethod
    def get_adapter(provider_name: str) -> BaseTicketAdapter:
        """
        Instantiates and returns the appropriate adapter for the given provider name.

        Args:
            provider_name (str): The name of the provider (case-sensitive keys).
                                 Supported: "HubSpot", "Jira", "Zendesk", "Salesforce".

        Returns:
            BaseTicketAdapter: An instance of a class that inherits from BaseTicketAdapter.

        Raises:
            ValueError: If the provider_name is not supported.
        """
        # Mapping of string identifiers to concrete Class types
        providers = {
            "HubSpot": HubSpotAdapter,
            "Jira": JiraAdapter,
            "Zendesk": ZendeskAdapter,
            "Salesforce": SalesforceAdapter
        }
        
        # Retrieve the class type from the map
        adapter_class = providers.get(provider_name)
        
        # Validation: Check if the provider exists in our mapping
        if not adapter_class:
            raise ValueError(f"Unsupported Provider: {provider_name}")
            
        # Return a new instance of the adapter
        return adapter_class()
