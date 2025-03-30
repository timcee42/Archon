"""
Security Analyst Agent for the EUC Assessment Team.

This agent is responsible for analyzing the security implications
of the proposed solution architecture.
"""

import json
import logging
import os
from typing import Dict, List, Optional, TypeVar, Any

from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from src.models.state import AssessmentState, SecurityConcern

logger = logging.getLogger(__name__)

# Type for the state
StateType = TypeVar("StateType", bound=AssessmentState)

# Pydantic model for structured output
class SecurityOutput(BaseModel):
    security_concerns: List[SecurityConcern] = Field(description="List of identified security concerns, including description, severity, and mitigation.")
    security_summary: str = Field(description="Overall summary of the security analysis and recommendations based on the provided architecture.")

# Instantiate the parser
security_parser = PydanticOutputParser(pydantic_object=SecurityOutput)

# Security Analyst system prompt
SECURITY_SYSTEM_PROMPT = f"""You are the Security Analyst Agent for an EUC (End User Computing) Assessment process.
Your responsibility is to analyze the security implications of the proposed solution architecture based on the assessment request, requirements, and context.

You should:
1. Analyze the provided architecture solution.
2. Identify potential security concerns (including description, severity: high|medium|low, and mitigation).
3. Provide an overall security summary and recommendations.

Focus on key security considerations in the EUC context:
- Data protection/privacy
- Identity/access management
- Endpoint security
- Network security
- Compliance
- Secure configuration/monitoring

{{format_instructions}}
"""

def _create_security_chain(llm):
    """Helper function to create the security agent LangChain chain."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SECURITY_SYSTEM_PROMPT.format(format_instructions=security_parser.get_format_instructions())),
            (
                "human",
                "Assessment request: {assessment_request}\n\n"
                + "Requirements: {requirements}\n\n"
                + "Organization context: {organization_context}\n\n"
                + "Architecture solution: {architecture_solution}\n\n"
                + "Please analyze the security implications of this architecture solution.",
            ),
        ]
    )
    
    chain = prompt | llm | security_parser
    return chain

def security_agent(state: StateType) -> StateType:
    """
    Security Analyst agent that performs security assessment.
    
    Args:
        state: The current state of the assessment
        
    Returns:
        Updated state with security concerns and summary
    """
    logger.info("Security Analyst agent invoked")
    
    # Initialize the LLM
    model_name = os.getenv("SECURITY_MODEL", "gpt-4")
    llm = ChatOpenAI(temperature=0, model_name=model_name)
    
    chain = _create_security_chain(llm)
    
    # Prepare the input for the chain
    chain_input = {
        "assessment_request": state.assessment_request,
        "requirements": state.requirements,
        "organization_context": state.organization_context,
        "architecture_solution": state.architecture_solution
    }
    
    # Execute the chain with the assessment data
    parsed_output: SecurityOutput = chain.invoke(chain_input)
    logger.debug(f"Parsed security response: {parsed_output}")
    
    # Extract security concerns
    state.security_concerns.extend(parsed_output.security_concerns)
    
    # Extract security summary
    state.security_summary = parsed_output.security_summary
    
    logger.info(f"Security Analyst agent completed. Identified {len(state.security_concerns)} security concerns")
    return state 