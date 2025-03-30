"""Support & Operations agent module for EUC Assessment Agent team.

This module contains the Support & Operations agent, responsible for analyzing
the implementation plan and defining support requirements, operational impact,
and ongoing maintenance needs.
"""

import json
import logging
from typing import Dict, List, Any, Optional

# Langchain imports
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
# Pydantic imports
from pydantic import BaseModel, Field

from src.config import get_settings
from src.models.state import (
    AssessmentState,
    SupportRequirement,
    OperationalImpact,
    MaintenanceTask
)

logger = logging.getLogger(__name__)

# --- Pydantic Output Model Definition ---
class SupportOperationsOutput(BaseModel):
    """Defines the structure for the support and operations analysis output."""
    support_requirements: List[SupportRequirement] = Field(description="List of support requirements for each component.")
    operational_impacts: List[OperationalImpact] = Field(description="List of operational impacts on existing systems and processes.")
    maintenance_tasks: List[MaintenanceTask] = Field(description="List of ongoing maintenance tasks and their schedules.")
    support_summary: str = Field(description="Overall summary of support and operations considerations.")

# Create a parser instance for the output model
parser = PydanticOutputParser(pydantic_object=SupportOperationsOutput)

# --- System Prompt Template ---
SUPPORT_OPERATIONS_SYSTEM_PROMPT = PromptTemplate(
    template=
"""
Analyze the provided assessment request and implementation plan to define a comprehensive support and operations plan.

Assessment Request:
{assessment_request}

Implementation Plan:
{implementation_plan_json}

Based on this information, generate:
1.  Support requirements for each component, including technical support needs, priority levels, necessary resources, and training requirements.
2.  Operational impacts on existing systems and processes, their severity, and mitigation strategies.
3.  Ongoing maintenance tasks with frequency, complexity, and required resources.
4.  An overall summary of support and operations considerations.

{format_instructions}
""",
    input_variables=["assessment_request", "implementation_plan_json"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Type alias for state
StateType = AssessmentState

# --- Helper function to create the LCEL chain ---
def _create_support_chain(llm: ChatOpenAI) -> Runnable:
    """Creates the Langchain Runnable for the support operations agent."""
    return SUPPORT_OPERATIONS_SYSTEM_PROMPT | llm | parser

def support_agent(state: StateType, messages: Optional[List[BaseMessage]] = None, testing: bool = False) -> StateType:
    """Support & Operations agent function.
    
    Args:
        state: The current assessment state
        messages: Optional list of previous messages (unused)
        testing: Flag for testing (skips LLM/chain initialization and invocation)
        
    Returns:
        Updated assessment state with support and operations plan
    """
    logger.info("Starting Support & Operations agent...")
    settings = get_settings()
    
    # Prepare implementation plan data for JSON serialization
    implementation_plan_json = "Not available"
    if state.implementation_plan:
        try:
            # Use model_dump_json for Pydantic V2 compatibility
            implementation_plan_json = state.implementation_plan.model_dump_json(indent=2)
        except Exception as e:
            logger.error(f"Error serializing implementation plan: {e}")
            implementation_plan_json = str(state.implementation_plan)

    if testing:
        logger.warning("Testing mode enabled, skipping LLM call.")
        # In testing mode, potentially return the state or a mock update
        return state

    # Initialize language model and chain
    try:
        llm = ChatOpenAI(
            model=settings.openai_model_name,
            temperature=settings.agent_temperature,
            api_key=settings.openai_api_key
        )
        support_chain = _create_support_chain(llm)
    except Exception as e:
        logger.error(f"Failed to initialize LLM or create Support chain: {e}")
        # Optionally set an error state or return the current state
        return state
        
    # Prepare input for the chain
    chain_input = {
        "assessment_request": state.assessment_request,
        "implementation_plan_json": implementation_plan_json
    }
    
    logger.debug(f"Invoking Support chain with input: {chain_input}")
    
    try:
        # Invoke the chain and parse the output
        support_output: SupportOperationsOutput = support_chain.invoke(chain_input)
        
        # Update the state with the parsed output
        state.support_requirements = support_output.support_requirements
        state.operational_impacts = support_output.operational_impacts
        state.maintenance_tasks = support_output.maintenance_tasks
        state.support_summary = support_output.support_summary
        
        logger.info("Successfully updated state with support and operations plan.")

    except Exception as e:
        logger.error(f"Error invoking Support chain or processing output: {e}")
        # Optionally set an error state or handle partial updates

    return state 