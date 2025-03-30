"""
Solution Architect Agent for the EUC Assessment Team.

This agent is responsible for designing the architecture solution based on
the research findings and requirements.
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

from src.models.state import (
    AssessmentState,
    ArchitectureSolution,
    ArchitectureComponent,
)

logger = logging.getLogger(__name__)

# Type for the state
StateType = TypeVar("StateType", bound=AssessmentState)

# Pydantic model for structured output
class ArchitectOutput(BaseModel):
    architecture_solution: ArchitectureSolution = Field(description="The detailed architecture solution, including overview, components, diagram description, and considerations.")

# Instantiate the parser
architect_parser = PydanticOutputParser(pydantic_object=ArchitectOutput)

# Solution Architect system prompt
ARCHITECT_SYSTEM_PROMPT = f"""You are the Solution Architect Agent for an EUC (End User Computing) Assessment process.
Your responsibility is to design an architecture solution based on the assessment request, requirements, and research findings.

You should:
1. Analyze the assessment request, requirements, organizational context, and research findings.
2. Design a comprehensive architecture solution that addresses the requirements.
3. Define key components, their purpose, description, and dependencies.
4. Provide a textual description of the solution architecture diagram.
5. List any additional considerations or alternatives evaluated.

{{format_instructions}}
"""

def _create_architect_chain(llm):
    """Helper function to create the architect agent LangChain chain."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", ARCHITECT_SYSTEM_PROMPT.format(format_instructions=architect_parser.get_format_instructions())),
            (
                "human",
                "Assessment request: {assessment_request}\n\n"
                + "Requirements: {requirements}\n\n"
                + "Organization context: {organization_context}\n\n"
                + "Research findings: {research_findings}\n\n"
                + "Research summary: {research_summary}\n\n"
                + "Please design an architecture solution for this assessment.",
            ),
        ]
    )
    
    chain = prompt | llm | architect_parser
    return chain

def architect_agent(state: StateType) -> StateType:
    """
    Solution Architect agent that designs an architecture solution.
    
    Args:
        state: The current state of the assessment
        
    Returns:
        Updated state with architecture solution
    """
    logger.info("Solution Architect agent invoked")
    
    # Initialize the LLM
    model_name = os.getenv("ARCHITECT_MODEL", "gpt-4")
    llm = ChatOpenAI(temperature=0, model_name=model_name)
    
    chain = _create_architect_chain(llm)
    
    # Prepare the input for the chain
    chain_input = {
        "assessment_request": state.assessment_request,
        "requirements": state.requirements,
        "organization_context": state.organization_context,
        "research_findings": state.research_findings,
        "research_summary": state.research_summary or "No research summary available."
    }
    
    # Execute the chain with the assessment data
    parsed_output: ArchitectOutput = chain.invoke(chain_input)
    logger.debug(f"Parsed architect response: {parsed_output}")
    
    # Extract architecture solution
    state.architecture_solution = parsed_output.architecture_solution
    
    logger.info(f"Solution Architect agent completed. Designed solution with {len(state.architecture_solution.components)} components")
    return state 