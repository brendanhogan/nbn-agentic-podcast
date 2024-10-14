"""

Utility functions, input etc. 

"""
import os
from typing import Type


from llm import LLM, GPT4O
from input import PDFInput, Input
from agentconfigs import AgentConfig, IraPod



def get_config_class(config_name: str) -> Type[AgentConfig]:
    """
    Returns the appropriate AgentConfig class based on the provided name.

    Args:
        config_name (str): The name of the configuration to use.

    Returns:
        Type[AgentConfig]: The class of the specified configuration.

    Raises:
        ValueError: If the configuration name is not supported.
    """
    if config_name.lower() == 'irapod':
        return IraPod
    else:
        raise ValueError(f"Configuration '{config_name}' is not supported.")


def get_input_processor(input_file: str) -> Input:
    """
    Identifies the input file type and returns the appropriate Input object.
    
    Args:
        input_file (str): Path to the input file.
    
    Returns:
        Input: An instance of the appropriate Input subclass.
    
    Raises:
        NotImplementedError: If the file type is not supported.
    """
    file_extension = os.path.splitext(input_file)[1].lower()
    
    if file_extension == '.pdf':
        return PDFInput(input_file)
    else:
        raise NotImplementedError(f"File type '{file_extension}' is not supported.")



def get_llm_instance(llm_type: str) -> LLM:
    """
    Returns the appropriate LLM instance based on the provided type.

    Args:
        llm_type (str): The type of LLM to instantiate.

    Returns:
        LLM: An instance of the specified LLM.

    Raises:
        NotImplementedError: If the LLM type is not supported.
    """
    if llm_type.lower() == 'gpt4o':
        return GPT4O()
    else:
        raise NotImplementedError(f"LLM type '{llm_type}' is not supported.")












#