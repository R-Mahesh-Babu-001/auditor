"""
Abstract base class for all agent types.
Defines the required interface for agent implementations.
"""

from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Base class for agents using LLMs.
    """
    def __init__(self, llm):
        self.llm = llm  # Language model instance

    @abstractmethod
    async def run(self, payload: dict) -> dict:
        """
        Run the agent with the given payload and return a result dict.
        """
        pass
