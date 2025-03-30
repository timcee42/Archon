"""Cost & Value Analyst agent module for EUC Assessment Agent team.

This module contains the Cost & Value Analyst agent, responsible for analyzing costs
and calculating ROI for the proposed solution.
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
    CostEstimate,
    ImplementationPlan,
    LicensingInfo,
    SupportRequirement,
    TrainingNeed,
)

logger = logging.getLogger(__name__)

# --- Pydantic Output Model Definition ---
class CostAnalysisOutput(BaseModel):
    """Defines the structure for the cost and value analysis output."""
    cost_estimates: List[CostEstimate] = Field(description="List of detailed cost estimates by category.")
    total_cost_estimate: float = Field(description="Overall total estimated cost.")
    roi_analysis: str = Field(description="Return on Investment (ROI) analysis with justification.")

# Create a parser instance for the output model
parser = PydanticOutputParser(pydantic_object=CostAnalysisOutput)

# --- System Prompt Template ---
COST_ANALYSIS_SYSTEM_PROMPT = PromptTemplate(
    template=
"""
Analyze the provided assessment details to create a comprehensive cost and value analysis for the proposed solution.

Assessment Request:
{assessment_request}

Implementation Plan:
{implementation_plan_json}

Licensing Information:
{licensing_info_json}

Support Requirements:
{support_requirements_json}

Training Needs:
{training_needs_json}

Based on all the information above, generate:
1.  Detailed cost estimates broken down by category (e.g., Licensing, Implementation, Support, Training, Hardware, Software, Migration, Operational). Include amounts, descriptions, and timeframes (e.g., one-time, per year).
2.  A calculated total cost estimate.
3.  A Return on Investment (ROI) analysis, clearly explaining the methodology, assumptions, and projected benefits (e.g., productivity gains, cost savings) that justify the investment over a specific period (e.g., 3 years).

{format_instructions}
""",
    input_variables=[
        "assessment_request",
        "implementation_plan_json",
        "licensing_info_json",
        "support_requirements_json",
        "training_needs_json"
    ],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Type alias for state
StateType = AssessmentState

# --- Helper function to create the LCEL chain ---
def _create_cost_chain(llm: ChatOpenAI) -> Runnable:
    """Creates the Langchain Runnable for the cost analysis agent."""
    return COST_ANALYSIS_SYSTEM_PROMPT | llm | parser

def cost_analysis_agent(state: StateType, messages: Optional[List[BaseMessage]] = None, testing: bool = False) -> StateType:
    """Cost & Value Analyst agent function.
    
    Args:
        state: The current assessment state
        messages: Optional list of previous messages (unused)
        testing: Flag for testing (skips LLM/chain initialization and invocation)
        
    Returns:
        Updated assessment state with cost and value analysis
    """
    logger.info("Starting Cost & Value Analyst agent...")
    settings = get_settings()
    
    # Helper function for safe JSON serialization
    def safe_serialize(data: Any, is_list: bool = False) -> str:
        default = "[]" if is_list else "Not available"
        if data is None:
            return default
        try:
            if is_list:
                # Handle lists of Pydantic models
                return json.dumps([item.model_dump() for item in data], indent=2)
            else:
                # Handle single Pydantic models
                return data.model_dump_json(indent=2)
        except AttributeError:
             # Handle cases where data might not be a Pydantic model or list thereof
            try:
                return json.dumps(data, indent=2) 
            except Exception as e:
                logger.error(f"Error during fallback JSON serialization: {e}")
                return str(data)
        except Exception as e:
            logger.error(f"Error serializing data: {e}")
            return str(data)

    # Prepare data for the prompt, ensuring it's JSON serialized
    implementation_plan_json = safe_serialize(state.implementation_plan)
    licensing_info_json = safe_serialize(state.licensing_info)
    support_requirements_json = safe_serialize(state.support_requirements, is_list=True)
    training_needs_json = safe_serialize(state.training_needs, is_list=True)

    if testing:
        logger.warning("Testing mode enabled, skipping LLM call.")
        # Provide mock data for testing if needed, or simply return the state
        # Example mock update (adjust as needed for actual test logic):
        # state.cost_estimates = [CostEstimate(category="Test", amount=1.0, description="Test Desc", timeframe="one-time")]
        # state.total_cost_estimate = 1.0
        # state.roi_analysis = "Test ROI Analysis"
        return state

    # Initialize language model and chain
    try:
        llm = ChatOpenAI(
            model=settings.openai_model_name,
            temperature=settings.agent_temperature,
            api_key=settings.openai_api_key
        )
        cost_chain = _create_cost_chain(llm)
    except Exception as e:
        logger.error(f"Failed to initialize LLM or create Cost chain: {e}")
        return state
        
    # Prepare input for the chain
    chain_input = {
        "assessment_request": state.assessment_request,
        "implementation_plan_json": implementation_plan_json,
        "licensing_info_json": licensing_info_json,
        "support_requirements_json": support_requirements_json,
        "training_needs_json": training_needs_json
    }
    
    logger.debug(f"Invoking Cost chain with input keys: {chain_input.keys()}")
    
    try:
        # Invoke the chain and parse the output
        cost_output: CostAnalysisOutput = cost_chain.invoke(chain_input)
        
        # Update the state with the parsed output
        state.cost_estimates = cost_output.cost_estimates
        state.total_cost_estimate = cost_output.total_cost_estimate
        state.roi_analysis = cost_output.roi_analysis
        
        logger.info("Successfully updated state with cost and value analysis.")

    except Exception as e:
        logger.error(f"Error invoking Cost chain or processing output: {e}")
        # Optionally set an error state or handle partial updates

    return state 