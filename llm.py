"""
This file defines the abstract base class for Language Model (LLM) interfaces and provides
a concrete implementation for GPT-4.0.

The LLM class is designed to be extensible, allowing for easy integration of different
language models while maintaining a consistent interface for model interactions.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
from openai import OpenAI

client = OpenAI()

class LLM(ABC):
    """
    Abstract base class for Language Model interfaces.

    This class defines the structure for interacting with various language models.
    Subclasses should implement the `call` method to handle specific model interactions.
    """

    @abstractmethod
    def call(self, conversations: List[Dict[str, str]], max_retries: int = 5, initial_wait: float = 1.0) -> Optional[str]:
        """
        Abstract method to make a call to the language model.

        Args:
            conversations (List[Dict[str, str]]): A list of dictionaries representing the conversation.
                Each dictionary should have two keys:
                - 'role': A string indicating the role of the speaker (e.g., 'system', 'user', 'assistant')
                - 'content': A string containing the message content
            max_retries (int): Maximum number of retry attempts.
            initial_wait (float): Initial wait time in seconds before retrying.

        Returns:
            Optional[str]: The response from the language model, or None if all retries fail.
        """
        pass

class GPT4O(LLM):
    """
    Concrete implementation of the LLM class for GPT-4.0.
    """

    def call(self, conversations: List[Dict[str, str]], max_retries: int = 5, initial_wait: float = 1.0) -> Optional[str]:
        """
        Make a call to the GPT-4.0 model with exponential backoff retry logic.

        Args:
            conversations (List[Dict[str, str]]): A list of dictionaries representing the conversation.
                Each dictionary should have two keys:
                - 'role': A string indicating the role of the speaker (e.g., 'system', 'user', 'assistant')
                - 'content': A string containing the message content
            max_retries (int): Maximum number of retry attempts.
            initial_wait (float): Initial wait time in seconds before retrying.

        Returns:
            Optional[str]: The response from the GPT-4.0 model as a string, or None if all retries fail.
        """
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversations
                )
                return response.choices[0].message.content
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to make GPT-4 call after {max_retries} attempts: {e}")
                    return None
                wait_time = initial_wait * (2 ** attempt)
                print(f"Error making GPT-4 call. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
