"""
Context & Requirements Agent for the EUC Assessment Team.

This agent is responsible for gathering the initial context and requirements
from the user for the EUC assessment.
"""

import json
import logging
from typing import Dict, List, Optional, TypeVar, Union, Any

# Import Pydantic models and Output Parsers
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from src.models.state import AssessmentState, Requirement, RequirementPriority, OrganizationContext

logger = logging.getLogger(__name__)

# Type for the state
StateType = TypeVar("StateType", bound=AssessmentState)

# Define Pydantic models for the expected output structure
# We reuse the existing Requirement and OrganizationContext models from state.py
class ContextOutput(BaseModel):
    requirements: List[Requirement] = Field(description="List of requirements extracted from the request")
    organization_context: OrganizationContext = Field(description="Organizational context extracted from the request")
    follow_up_questions: List[str] = Field(description="List of questions to ask the user for missing information")

# Create an instance of the output parser
context_parser = PydanticOutputParser(pydantic_object=ContextOutput)

# Context and Requirements system prompt (simplified to work with parser)
CONTEXT_SYSTEM_PROMPT = """You are the Context & Requirements Agent for an EUC (End User Computing) Assessment process.
Your responsibility is to gather initial context and requirements from the user's assessment request.

The user has submitted a request for an EUC assessment. Your task is to:
1. Extract clear requirements from the request
2. Identify any organization-specific context that is relevant to the assessment
3. Identify any missing information that would be important for a complete assessment

Format your response according to the provided instructions.
"""

# Follow-up system prompt to interact with the user
FOLLOWUP_SYSTEM_PROMPT = """You are the Context & Requirements Agent for an EUC (End User Computing) Assessment.
Based on the initial assessment request, you've identified some follow-up questions to gather important missing information.

Please ask these questions to the user in a conversational manner. Explain why this information is important for the assessment.
After receiving the user's response, update your understanding of the requirements and context accordingly.
"""


def context_prompt() -> ChatPromptTemplate:
    """Create the prompt for the context and requirements agent."""
    return ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(CONTEXT_SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(
                "Assessment request: {assessment_request}\n\n{format_instructions}",
            ),
        ],
        input_variables=["assessment_request"],
        partial_variables={"format_instructions": context_parser.get_format_instructions()}
    )


def followup_prompt() -> ChatPromptTemplate:
    """Create the prompt for follow-up questions."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", FOLLOWUP_SYSTEM_PROMPT),
            (
                "human",
                "Based on the assessment request: {assessment_request}\n\nI need to ask the following follow-up questions: {follow_up_questions}",
            ),
        ]
    )


def parse_context_response(response: str) -> Dict[str, Any]:
    """
    Parse the response from the context agent.
    
    Args:
        response: The response string from the LLM
        
    Returns:
        Parsed JSON as a dictionary
    """
    try:
        # Try to parse the JSON response
        return json.loads(response)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse context agent response as JSON: {e}")
        logger.error(f"Raw response: {response}")
        # Return a minimal valid structure as fallback
        return {
            "requirements": [],
            "organization_context": {},
            "follow_up_questions": []
        }


def create_requirements_from_json(json_data: Dict[str, Any]) -> List[Requirement]:
    """
    Create Requirement objects from parsed JSON data.
    
    Args:
        json_data: Parsed JSON data containing requirements
        
    Returns:
        List of Requirement objects
    """
    requirements = []
    
    for req_data in json_data.get("requirements", []):
        priority_str = req_data.get("priority", "medium").lower()
        
        # Map the priority string to the RequirementPriority enum
        if priority_str == "high":
            priority = RequirementPriority.HIGH
        elif priority_str == "low":
            priority = RequirementPriority.LOW
        else:
            priority = RequirementPriority.MEDIUM
            
        requirement = Requirement(
            description=req_data.get("description", ""),
            priority=priority,
            notes=req_data.get("notes")
        )
        requirements.append(requirement)
        
    return requirements


def create_org_context_from_json(json_data: Dict[str, Any]) -> OrganizationContext:
    """
    Create an OrganizationContext object from parsed JSON data.
    
    Args:
        json_data: Parsed JSON data containing organization context
        
    Returns:
        OrganizationContext object
    """
    org_data = json_data.get("organization_context", {})
    
    return OrganizationContext(
        company_size=org_data.get("company_size"),
        industry=org_data.get("industry"),
        current_tech_stack=org_data.get("current_tech_stack"),
        compliance_requirements=org_data.get("compliance_requirements"),
        additional_context=org_data.get("additional_context")
    )


def _create_context_chain(llm, parser):
    """Helper function to create the context agent's LCEL chain."""
    prompt = context_prompt()
    chain = (
        prompt
        | llm
        | parser
    )
    return chain


def context_agent(state: StateType, messages: Optional[List[BaseMessage]] = None) -> StateType:
    """
    Context & Requirements agent that gathers initial context for the assessment.
    Uses PydanticOutputParser for structured output.

    Args:
        state: The current state of the assessment
        messages: Optional messages from the user with additional context

    Returns:
        Updated state with requirements and context information
    """
    logger.info("Context agent invoked")

    # Initialize the LLM
    # Note: Ensure model supports function calling or structured output for best results with PydanticOutputParser
    llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo-preview") # Example model known to work well

    # Create the chain using the helper function
    chain = _create_context_chain(llm, context_parser)

    # Execute the chain with the assessment request
    try:
        parsed_response: ContextOutput = chain.invoke({"assessment_request": state.assessment_request})
        logger.debug(f"Parsed context response: {parsed_response}")

        # Update state directly from the parsed Pydantic object
        state.requirements.extend(parsed_response.requirements)
        state.organization_context = parsed_response.organization_context

        # Handle follow-up questions
        follow_up_questions = parsed_response.follow_up_questions
        if follow_up_questions:
            logger.info(f"Follow-up questions identified: {follow_up_questions}")
            # TODO: Implement logic to actually ask these questions

        logger.info(f"Context agent completed. Extracted {len(parsed_response.requirements)} requirements")

    except Exception as e:
        logger.error(f"Error in context agent chain execution or parsing: {e}")
        # Optionally handle the error, e.g., set an error state or return without updates

    return state 