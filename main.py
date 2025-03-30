"""
Main application script for the EUC Assessment Agent Team.

This script initializes the LangGraph workflow and defines the
connections between the various agents.
"""

import logging
import os
from typing import Dict, List, Annotated, TypedDict, Any, Optional

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import HumanMessage, AIMessage

from src.agents.orchestrator import orchestrator_agent
from src.agents.context import context_agent
from src.agents.research import research_agent
from src.agents.architect import architect_agent
from src.agents.security import security_agent
from src.agents.licensing import licensing_agent
from src.agents.implementation import implementation_agent
from src.models.state import AssessmentState
from src.agents.support import support_agent
from src.agents.user_experience import user_experience_agent
from src.agents.cost_analysis import cost_analysis_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def create_workflow() -> StateGraph:
    """
    Build and configure the agent workflow graph.
    
    Returns:
        StateGraph: The configured workflow graph
    """
    logger.info("Building EUC Assessment Agent workflow graph")
    
    # Create a new graph
    workflow = StateGraph(AssessmentState)
    
    # Add nodes
    workflow.add_node("orchestrator", orchestrator_agent)
    workflow.add_node("context_requirements", context_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("architecture", architect_agent)
    workflow.add_node("security", security_agent)
    workflow.add_node("licensing", licensing_agent)
    workflow.add_node("implementation", implementation_agent)
    workflow.add_node("support", support_agent)
    workflow.add_node("user_experience", user_experience_agent)
    workflow.add_node("cost_analysis", cost_analysis_agent)
    
    # Define edges - each agent returns to the orchestrator for next steps
    workflow.add_edge("context_requirements", "orchestrator")
    workflow.add_edge("research", "orchestrator")
    workflow.add_edge("architecture", "orchestrator")
    workflow.add_edge("security", "orchestrator")
    workflow.add_edge("licensing", "orchestrator")
    workflow.add_edge("implementation", "orchestrator")
    workflow.add_edge("support", "orchestrator")
    workflow.add_edge("user_experience", "orchestrator")
    workflow.add_edge("cost_analysis", "orchestrator")
    
    # Conditional routing based on current_phase in state
    def route_by_phase(state: AssessmentState) -> str:
        """Route to the next agent based on the current phase."""
        if state.current_phase == "initial":
            return "research"
        elif state.current_phase == "research_complete":
            return "architecture"
        elif state.current_phase == "architecture_complete":
            return "security"
        elif state.current_phase == "security_complete":
            return "licensing"
        elif state.current_phase == "licensing_complete":
            return "implementation"
        elif state.current_phase == "implementation_complete":
            return "support"
        elif state.current_phase == "support_complete":
            return "user_experience"
        elif state.current_phase == "user_experience_complete":
            return "cost_analysis"
        elif state.current_phase == "cost_analysis_complete":
            return "end"
        else:
            return "orchestrator"
    
    workflow.add_conditional_edges(
        "orchestrator",
        route_by_phase,
        {
            "research": "research",
            "architecture": "architecture",
            "security": "security",
            "licensing": "licensing",
            "implementation": "implementation",
            "support": "support",
            "user_experience": "user_experience",
            "cost_analysis": "cost_analysis",
            "end": END,
            # Additional phases will be added as we implement more agents
        },
    )
    
    # Set the entry point
    workflow.set_entry_point("orchestrator")
    
    logger.info("Graph building complete")
    return workflow


def run_assessment(
    assessment_request: str,
    client_name: Optional[str] = None,
    project_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run an EUC assessment with the given request.
    
    Args:
        assessment_request: The assessment request text
        client_name (Optional[str], optional): Name of the client. Defaults to None.
        project_name (Optional[str], optional): Name of the project. Defaults to None.
        
    Returns:
        Dict[str, Any]: The final state after assessment completion
    """
    logger.info(f"Starting assessment with request: {assessment_request}")
    
    # Build the workflow graph
    graph = create_workflow()
    
    # Initialize the state
    state = AssessmentState(
        assessment_request=assessment_request,
        client_name=client_name,
        project_name=project_name,
    )
    
    # Execute the graph
    config = {"recursion_limit": 100}  # Prevent infinite loops
    result = graph.invoke(state, config=config)
    
    logger.info("Assessment completed")
    return result.dict()


if __name__ == "__main__":
    # Example assessment request
    example_request = """
    We need to assess the feasibility of migrating our file shares to Microsoft OneDrive.
    We have approximately 5,000 employees across 3 locations, and our current file shares
    are hosted on Windows File Servers. We're especially concerned about security, user
    adoption, and the migration process.
    """
    
    # Run the assessment
    final_state = run_assessment(example_request)
    
    # Print the final report
    if final_state.final_report:
        print("\n--- Final Assessment Report ---\n")
        print(final_state.final_report)
    else:
        print("\n--- Assessment Results ---\n")
        print(f"Requirements identified: {len(final_state.requirements)}")
        print(f"Research topics: {len(final_state.research_findings)}")
        
        # Print additional results as they become available
        if final_state.architecture_solution:
            print(f"Architecture solution: {final_state.architecture_solution.overview}")
            
        if final_state.security_summary:
            print(f"Security summary: {final_state.security_summary}")
            
        if final_state.licensing_info:
            print(f"Licensing model: {final_state.licensing_info.model}")
            
        if final_state.implementation_summary:
            print(f"Implementation plan: {final_state.implementation_summary}")
            print(f"Number of implementation steps: {len(final_state.implementation_steps)}")
            
        # Include other summaries as they become available 