"""User Experience & Enablement agent module for EUC Assessment Agent team.

This module contains the User Experience & Enablement agent, responsible for analyzing
user impacts and creating enablement plans for the proposed solution.
"""

import json
import logging
from typing import Dict, List, Any, Optional

# Langchain imports
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
# Pydantic imports
from pydantic import BaseModel, Field

from src.config import get_settings
from src.models.state import (
    AssessmentState,
    UserImpact,
    TrainingNeed,
    AdoptionPlan,
    ChangeImpact
)

logger = logging.getLogger(__name__)

# --- Pydantic Output Model Definition ---
class UserExperienceOutput(BaseModel):
    """Defines the structure for the user experience analysis output."""
    user_impacts: List[UserImpact] = Field(description="List of impacts on different user groups.")
    training_needs: List[TrainingNeed] = Field(description="List of identified training needs.")
    adoption_plan: AdoptionPlan = Field(description="Plan for solution adoption.")
    change_impacts: List[ChangeImpact] = Field(description="List of overall change impacts.")
    user_experience_summary: str = Field(description="Overall summary of user experience and enablement.")

# Create a parser instance for the output model
parser = PydanticOutputParser(pydantic_object=UserExperienceOutput)

# --- System Prompt Template ---
USER_EXPERIENCE_SYSTEM_PROMPT = PromptTemplate(
    template=
"""
Analyze the provided assessment request and implementation plan to evaluate user experience impacts and devise a comprehensive enablement plan.

Assessment Request:
{assessment_request}

Implementation Plan:
{implementation_plan_json}

Based on this information, generate:
1.  Detailed impacts on various user groups.
2.  Specific training needs and requirements.
3.  A phased adoption plan including activities and success metrics.
4.  Potential change impacts, their severity, and mitigation strategies.
5.  An overall summary of the user experience and enablement considerations.

{format_instructions}
""",
    input_variables=["assessment_request", "implementation_plan_json"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)


# Type alias for state
StateType = AssessmentState

# --- Helper function to create the LCEL chain ---
def _create_ux_chain(llm: ChatOpenAI) -> Runnable:
    """Creates the Langchain Runnable for the user experience agent."""
    return USER_EXPERIENCE_SYSTEM_PROMPT | llm | parser


def user_experience_agent(state: StateType, messages: Optional[List[BaseMessage]] = None, testing: bool = False) -> StateType:
    """User Experience & Enablement agent function.
    
    Args:
        state: The current assessment state
        messages: Optional list of previous messages (unused)
        testing: Flag for testing (skips LLM/chain initialization and invocation)
        
    Returns:
        Updated assessment state with user experience and enablement plan
    """
    logger.info("Starting User Experience & Enablement agent...")
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
        ux_chain = _create_ux_chain(llm)
    except Exception as e:
        logger.error(f"Failed to initialize LLM or create UX chain: {e}")
        # Optionally set an error state or return the current state
        return state
        
    # Prepare input for the chain
    chain_input = {
        "assessment_request": state.assessment_request,
        "implementation_plan_json": implementation_plan_json
    }
    
    logger.debug(f"Invoking UX chain with input: {chain_input}")
    
    try:
        # Invoke the chain and parse the output
        ux_output: UserExperienceOutput = ux_chain.invoke(chain_input)
        
        # Update the state with the parsed output
        state.user_impacts = ux_output.user_impacts
        state.training_needs = ux_output.training_needs
        state.adoption_plan = ux_output.adoption_plan
        state.change_impacts = ux_output.change_impacts
        state.user_experience_summary = ux_output.user_experience_summary
        
        logger.info("Successfully updated state with user experience plan.")

    except Exception as e:
        logger.error(f"Error invoking UX chain or processing output: {e}")
        # Optionally set an error state or handle partial updates
        # For now, just log the error and return the potentially partially updated state

    return state 