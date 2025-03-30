"""
Lead Orchestrator Agent for the EUC Assessment Team.

This agent is responsible for coordinating the workflow between the specialized agents,
managing state transitions, and ensuring the assessment process follows the intended flow.
"""

import logging
from typing import Dict, List, Optional, TypeVar

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate

from src.models.state import AssessmentState

logger = logging.getLogger(__name__)

# Type for the state
StateType = TypeVar("StateType", bound=AssessmentState)

# Orchestrator system prompt
ORCHESTRATOR_SYSTEM_PROMPT = """You are the Lead Orchestrator for an EUC (End User Computing) Assessment process.
Your responsibility is to coordinate the workflow of specialized agents, determine which agent should work on the assessment next,
and ensure the overall assessment process runs smoothly.

Based on the current state of the assessment, you will:
1. Determine which phase of the assessment should be executed next
2. Prepare the relevant information for the next agent
3. Update the workflow control information

The assessment follows this general workflow:
1. Context & Requirements gathering (initial phase)
2. Research & Feasibility analysis
3. Solution Architecture design
4. Parallel specialist analysis (Security, Licensing, Implementation planning)
5. Additional specialist analysis (Support, User Experience, Cost)
6. Final report generation

You will be provided with the current state of the assessment. Your task is to determine the next phase
and update the 'current_phase' field accordingly. The possible phases are:
- "context_requirements" - For gathering initial context and requirements
- "research" - For performing research on the topic
- "architecture" - For designing the solution architecture
- "security" - For security analysis
- "licensing" - For licensing analysis
- "implementation" - For implementation planning
- "support" - For support and operations planning
- "user_experience" - For user experience and enablement planning
- "cost" - For cost and value analysis
- "report" - For final report generation
- "complete" - When the assessment is complete

Respond with a JSON object containing:
1. "next_phase": The next phase to execute
2. "reasoning": Your reasoning for choosing this phase
3. "instructions": Specific instructions for the agent in this phase (what they should focus on)
"""


def orchestrator_prompt() -> ChatPromptTemplate:
    """Create the prompt for the orchestrator agent."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", ORCHESTRATOR_SYSTEM_PROMPT),
            (
                "human",
                "Current assessment state: {state}\n\nBased on this state, determine the next phase of the assessment.",
            ),
        ]
    )


def orchestrator(state: StateType, messages: Optional[List[BaseMessage]] = None) -> StateType:
    """
    Lead Orchestrator agent that determines the next step in the assessment workflow.

    Args:
        state: The current state of the assessment
        messages: Optional messages from the previous agent

    Returns:
        Updated state with the next phase determined
    """
    logger.info(f"Orchestrator invoked. Current phase: {state.current_phase}")

    # Handle the initial state ("init") or if phase is somehow None
    if state.current_phase == "init" or state.current_phase is None:
        logger.info("Initial orchestrator invocation or 'init' state found. Setting phase to context_requirements")
        state.current_phase = "context_requirements"
        return state # Return immediately after setting the first phase

    # Determine next phase based on completed phases and state content
    # This is a simple sequential logic for now, to be expanded later
    if state.current_phase == "context_requirements" and state.requirements:
        # If we have gathered requirements, move to research
        if "context_requirements" not in state.completed_phases:
            state.completed_phases.append("context_requirements")
        state.current_phase = "research"
        logger.info("Moving to research phase")
    
    elif state.current_phase == "research" and state.research_findings:
        # If we have research findings, move to architecture
        if "research" not in state.completed_phases:
            state.completed_phases.append("research")
        state.current_phase = "architecture"
        logger.info("Moving to architecture phase")
    
    elif state.current_phase == "architecture" and state.architecture_solution:
        # If we have an architecture solution, start specialist assessments with security
        if "architecture" not in state.completed_phases:
            state.completed_phases.append("architecture")
        state.current_phase = "security"
        logger.info("Moving to security phase")
    
    elif state.current_phase == "security" and state.security_summary:
        # After security analysis, move to licensing
        if "security" not in state.completed_phases:
            state.completed_phases.append("security")
        state.current_phase = "licensing"
        logger.info("Moving to licensing phase")
    
    elif state.current_phase == "licensing" and state.licensing_info:
        # After licensing analysis, move to implementation planning
        if "licensing" not in state.completed_phases:
            state.completed_phases.append("licensing")
        state.current_phase = "implementation"
        logger.info("Moving to implementation phase")
    
    elif state.current_phase == "implementation" and state.implementation_summary:
        # After implementation planning, move to support planning
        if "implementation" not in state.completed_phases:
            state.completed_phases.append("implementation")
        state.current_phase = "support"
        logger.info("Moving to support phase")
    
    elif state.current_phase == "support" and state.support_summary:
        # After support planning, move to user experience
        if "support" not in state.completed_phases:
            state.completed_phases.append("support")
        state.current_phase = "user_experience"
        logger.info("Moving to user experience phase")
    
    elif state.current_phase == "user_experience" and state.user_experience_summary:
        # After user experience, move to cost analysis
        if "user_experience" not in state.completed_phases:
            state.completed_phases.append("user_experience")
        state.current_phase = "cost"
        logger.info("Moving to cost phase")
    
    elif state.current_phase == "cost" and state.roi_analysis:
        # After cost analysis, move to final report generation
        if "cost" not in state.completed_phases:
            state.completed_phases.append("cost")
        state.current_phase = "report"
        logger.info("Moving to report generation phase")
    
    elif state.current_phase == "report" and state.final_report:
        # After report generation, the assessment is complete
        if "report" not in state.completed_phases:
            state.completed_phases.append("report")
        state.current_phase = "complete"
        logger.info("Assessment complete")
    
    # Add future phase transitions as needed
    
    logger.info(f"Orchestrator completed. Next phase: {state.current_phase}")
    return state 