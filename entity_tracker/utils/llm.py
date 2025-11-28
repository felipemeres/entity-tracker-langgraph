"""
LLM utility functions for creating and configuring language models.

This module provides utilities for creating LLM instances with fallback support.
"""

from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel


async def create_llm_from_config(
    llm_config: Dict[str, Any], 
    output_schema: Optional[Any] = None
) -> BaseChatModel:
    """
    Create an LLM instance from a configuration dictionary.
    
    Args:
        llm_config: Dictionary with 'name', 'temperature', 'fallback_model'
        output_schema: Optional Pydantic schema for structured output
        
    Returns:
        Configured LLM instance with optional structured output
    """
    model_name = llm_config["name"]
    temperature = llm_config.get("temperature", 0.0)
    
    # Extract provider and model from format "provider/model"
    if "/" in model_name:
        provider, model = model_name.split("/", 1)
    else:
        provider = "openai"
        model = model_name
    
    # For this simplified version, we'll use OpenAI
    # In a production version, you'd add support for multiple providers
    if provider == "openai":
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
        )
    else:
        # Default to OpenAI for unsupported providers
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=temperature,
        )
    
    # Add structured output if schema provided
    if output_schema:
        llm = llm.with_structured_output(output_schema)
    
    return llm


def create_llm_configs(configurable: Any) -> Dict[str, Dict[str, Any]]:
    """
    Create LLM configurations dictionary from configurable object.
    
    Args:
        configurable: Configuration object with LLM settings
        
    Returns:
        Dictionary of LLM configurations for different complexity levels
    """
    return {
        "llm_query_creator": {
            "name": configurable.llm_query_creator,
            "temperature": configurable.llm_query_creator_temperature,
            "fallback_model": configurable.llm_query_creator_fallback_model
        },
        "llm_reviewer": {
            "name": configurable.llm_reviewer,
            "temperature": configurable.llm_reviewer_temperature,
            "fallback_model": configurable.llm_reviewer_fallback_model
        },
        "llm_writer": {
            "name": configurable.llm_writer,
            "temperature": configurable.llm_writer_temperature,
            "fallback_model": configurable.llm_writer_fallback_model
        }
    }

