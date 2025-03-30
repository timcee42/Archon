"""
Licensing Specialist Agent for the EUC Assessment Team.

This agent is responsible for analyzing the licensing implications
of the proposed solution architecture.
"""

import json
import logging
import os
from typing import Dict, List, Optional, TypeVar, Any

from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.models.state import AssessmentState, LicensingInfo

logger = logging.getLogger(__name__)

# Type for the state
StateType = TypeVar("StateType", bound=AssessmentState)

# --- Pydantic Output Model Definition ---
class LicensingOutput(BaseModel):
    """Pydantic model for the structured output of the Licensing Specialist Agent."""
    licensing_info: LicensingInfo = Field(..., description="Detailed licensing information including model, costs, constraints, and recommendations.")

# Create the parser instance
licensing_parser = PydanticOutputParser(pydantic_object=LicensingOutput)

# --- Updated System Prompt --- 
# Incorporates parser instructions and removes manual JSON example
LICENSING_SYSTEM_PROMPT = f"""You are the Licensing Specialist Agent for an EUC (End User Computing) Assessment process.
Your responsibility is to analyze the licensing implications of the proposed solution architecture.

You should:
1. Identify the licensing models applicable to the proposed solution
2. Estimate licensing costs based on the organization context
3. Identify any licensing constraints or compliance issues
4. Provide licensing recommendations to optimize costs and compliance

Focus on key licensing considerations in the EUC context, such as:
- Software licensing models (subscription, perpetual, per-user, per-device)
- Volume licensing agreements and options
- Enterprise agreements that might apply
- Open source vs. commercial licensing implications
- Compliance requirements and audit risks
- Cost optimization strategies

{{format_instructions}}
"""

# --- Chain Creation Helper Function --- 
def _create_licensing_chain(llm: ChatOpenAI):
    """Helper function to create the licensing agent chain."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", LICENSING_SYSTEM_PROMPT),
            (
                "human",
                "Assessment request: {{assessment_request}}\n\n"
                + "Requirements: {{requirements}}\n\n"
                + "Organization context: {{organization_context}}\n\n"
                + "Architecture solution: {{architecture_solution}}\n\n"
                + "Please analyze the licensing implications of this architecture solution.",
            ),
        ]
    ).partial(format_instructions=licensing_parser.get_format_instructions())
    
    return prompt | llm | licensing_parser


# --- Remove old parsing functions ---
# def parse_licensing_response(response: str) -> Dict[str, Any]: ...
# def create_licensing_info_from_json(json_data: Dict[str, Any]) -> LicensingInfo: ...


# --- Refactored Agent Function ---
def licensing_agent(state: StateType, messages: Optional[List[BaseMessage]] = None) -> StateType:
    """Licensing Specialist agent that performs licensing assessment using PydanticOutputParser.
    
    Args:
        state: The current state of the assessment
        messages: Optional messages from the previous agent (unused)
        
    Returns:
        Updated state with licensing information
    """
    logger.info("Licensing Specialist agent invoked")
    
    # Initialize the LLM
    # TODO: Add configuration from settings
    model_name = os.getenv("LICENSING_MODEL", "gpt-4") 
    llm = ChatOpenAI(temperature=0, model_name=model_name)
    
    # Create the chain using the helper
    chain = _create_licensing_chain(llm)
    
    # Prepare the input for the chain
    chain_input = {
        "assessment_request": state.assessment_request,
        "requirements": state.requirements,
        "organization_context": state.organization_context,
        "architecture_solution": state.architecture_solution
    }
    
    # Execute the chain with the assessment data
    # The output is now a parsed LicensingOutput object
    parsed_output: LicensingOutput = chain.invoke(chain_input) 
    logger.debug(f"Parsed licensing output: {parsed_output}")
    
    # Update state directly with the parsed object's content
    state.licensing_info = parsed_output.licensing_info
    
    logger.info("Licensing Specialist agent completed")
    return state 