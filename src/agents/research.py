"""
Research & Feasibility Agent for the EUC Assessment Team.

This agent is responsible for gathering information about the assessment topic,
researching potential solutions, and evaluating their feasibility.
"""

import json
import logging
from typing import Dict, List, Optional, TypeVar, Any

from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

from src.models.state import AssessmentState, ResearchFinding

logger = logging.getLogger(__name__)

# Type for the state
StateType = TypeVar("StateType", bound=AssessmentState)

# Pydantic model for structured output
class ResearchOutput(BaseModel):
    research_findings: List[ResearchFinding] = Field(description="List of detailed research findings for each topic investigated.")
    research_summary: str = Field(description="Overall summary of research findings and feasibility assessment related to the assessment request.")

# Instantiate the parser
research_parser = PydanticOutputParser(pydantic_object=ResearchOutput)

# Research and Feasibility system prompt
RESEARCH_SYSTEM_PROMPT = f"""You are the Research & Feasibility Agent for an EUC (End User Computing) Assessment process.
Your responsibility is to gather information about the assessment topic, research potential solutions, and evaluate their feasibility.

You have access to a web search tool to find relevant information. You should:
1. Analyze the assessment request, requirements, and organizational context.
2. Identify key topics that need research based on the inputs.
3. Conduct searches to gather relevant information for those topics.
4. Summarize your findings and evaluate the feasibility of potential solutions based *only* on the information gathered.

Provide detailed findings for each topic researched, including content, sources, and relevance.
Conclude with an overall summary.

{{format_instructions}}
"""

def _create_research_chain(llm):
    """Helper function to create the research agent LangChain chain."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RESEARCH_SYSTEM_PROMPT.format(format_instructions=research_parser.get_format_instructions())),
            (
                "human",
                "Assessment request: {assessment_request}\n\n"
                + "Requirements: {requirements}\n\n"
                + "Organization context: {organization_context}\n\n"
                + "Please conduct research on this topic and evaluate feasibility.",
            ),
        ]
    )
    
    chain = prompt | llm | research_parser
    return chain

def research_agent(state: StateType) -> StateType:
    """
    Research & Feasibility agent that gathers information about the assessment topic.
    
    Args:
        state: The current state of the assessment
        
    Returns:
        Updated state with research findings
    """
    logger.info("Research agent invoked")
    
    # Initialize the search tool (Note: Not currently bound to the chain)
    search_tool = DuckDuckGoSearchRun()
    
    # Initialize the LLM
    llm = ChatOpenAI(temperature=0, model_name="gpt-4")
    
    # Create the chain for research and feasibility analysis
    chain = _create_research_chain(llm)
    
    # Prepare the input for the chain
    chain_input = {
        "assessment_request": state.assessment_request,
        "requirements": state.requirements,
        "organization_context": state.organization_context
    }
    
    # Execute the chain with the assessment request and context
    parsed_response: ResearchOutput = chain.invoke(chain_input)
    logger.debug(f"Parsed research response: {parsed_response}")
    
    # Extract research findings
    state.research_findings.extend(parsed_response.research_findings)
    
    # Extract research summary
    state.research_summary = parsed_response.research_summary
    
    logger.info(f"Research agent completed. Found {len(parsed_response.research_findings)} research topics")
    return state 