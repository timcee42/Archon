"""Implementation Engineer agent module for EUC Assessment Agent team.

This module contains the Implementation Engineer agent, responsible for developing 
an implementation plan based on the architecture solution, security analysis,
and licensing information.
"""

import json
import logging
from typing import Dict, List, Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI

from src.config import get_settings
from src.models.state import AssessmentState, ImplementationStep, ImplementationPlan

logger = logging.getLogger(__name__)

# Type alias for state
StateType = AssessmentState


def _extract_implementation_data(response_content: str) -> Dict[str, Any]:
    """Extract implementation data from the response content."""
    try:
        # Try to parse entire content as JSON
        return json.loads(response_content)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON from the text
        try:
            start_idx = response_content.find("{")
            end_idx = response_content.rfind("}")
            if start_idx != -1 and end_idx != -1:
                json_str = response_content[start_idx:end_idx + 1]
                return json.loads(json_str)
            return {}
        except (json.JSONDecodeError, ValueError):
            logger.error(f"Failed to parse response: {response_content}")
            return {}


def _process_implementation_steps(data: Dict[str, Any]) -> List[ImplementationStep]:
    """Process implementation steps from the extracted data."""
    steps = []
    if "implementation_steps" in data:
        for step_data in data["implementation_steps"]:
            try:
                step = ImplementationStep(**step_data)
                steps.append(step)
            except Exception as e:
                logger.error(f"Error creating implementation step: {e}")
    return steps


def create_implementation_prompt(state: AssessmentState) -> str:
    """Create a prompt for the Implementation Engineer agent."""
    
    # Prepare data for JSON serialization
    architecture_data = "Not available"
    if state.architecture_solution:
        try:
            architecture_data = json.dumps(state.architecture_solution.model_dump(), indent=2)
        except Exception:
            architecture_data = str(state.architecture_solution)
    
    security_data = "Not available"
    try:
        security_data = json.dumps([concern.model_dump() for concern in state.security_concerns], indent=2)
    except Exception:
        security_data = str(state.security_concerns)
    
    licensing_data = "Not available"
    if state.licensing_info:
        try:
            licensing_data = json.dumps(state.licensing_info.model_dump(), indent=2)
        except Exception:
            licensing_data = str(state.licensing_info)
    
    # Create the example JSON structure (no f-string needed)
    json_example = """```json
    {
        "implementation_plan": {
            "summary": "Implementation summary here",
            "steps": [
                {
                    "order": 1,
                    "title": "Step title",
                    "description": "Step description",
                    "dependencies": [0],
                    "estimated_effort": "Effort estimate",
                    "resources_required": ["Resource 1"],
                    "risk_factors": ["Risk 1"]
                }
            ],
            "timeline_estimate": "Timeline estimate",
            "critical_path": ["Critical step 1"]
        }
    }
    ```"""
    
    # Build the prompt in parts to avoid nested f-strings
    prompt = f"""
    Please analyze the architecture solution, security concerns, and licensing information
    provided below to create a comprehensive implementation plan.
    
    Assessment Request: {state.assessment_request}
    
    Architecture Solution:
    {architecture_data}
    
    Security Concerns:
    {security_data}
    
    Licensing Information:
    {licensing_data}
    
    Based on this information, create a detailed implementation plan that includes:
    1. A summary of the implementation approach
    2. Step-by-step implementation tasks
    3. Dependencies between tasks
    4. Estimated effort for each task
    5. Resources required
    6. Risk factors to be aware of
    7. Overall timeline estimate
    8. Critical path items
    
    Format your response as a JSON object with the structure shown in the example below.
    Example structure (replace with actual content):
    """
    
    # Combine the parts
    prompt += json_example
    
    return prompt


def parse_implementation_plan(response_text: str) -> Dict[str, Any]:
    """Parse the implementation plan from JSON response."""
    try:
        # Extract JSON from the response text (handling potential text before/after JSON)
        response_text = response_text.strip()
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        
        # Fallback if no JSON detected
        return {"implementation_plan": {"summary": "Error parsing implementation plan", "steps": []}}
        
    except json.JSONDecodeError:
        return {"implementation_plan": {"summary": "Error parsing implementation plan", "steps": []}}


def create_implementation_steps(steps_data: List[Dict[str, Any]]) -> List[ImplementationStep]:
    """Create ImplementationStep objects from JSON data."""
    implementation_steps = []
    
    for step_data in steps_data:
        step = ImplementationStep(
            order=step_data.get("order", 0),
            title=step_data.get("title", "Unknown step"),
            description=step_data.get("description", ""),
            estimated_effort=step_data.get("estimated_effort"),
            dependencies=step_data.get("dependencies"),
            resources_required=step_data.get("resources_required", []),
            risk_factors=step_data.get("risk_factors", [])
        )
        implementation_steps.append(step)
    
    return implementation_steps


def implementation_agent(state: StateType, messages: Optional[List[BaseMessage]] = None, testing: bool = False) -> StateType:
    """Implementation Engineer agent function.
    
    Args:
        state: The current assessment state
        messages: Optional list of previous messages (unused)
        testing: Flag for testing (skips LLM initialization)
        
    Returns:
        Updated assessment state with implementation plan
    """
    settings = get_settings()
    
    # Initialize language model
    if not testing:
        llm = ChatOpenAI(
            model=settings.openai_model_name,
            temperature=settings.agent_temperature,
            api_key=settings.openai_api_key
        )
        
        # Create implementation engineer system prompt
        system_prompt = """You are the Implementation Engineer in an EUC assessment team.
        Your role is to analyze the architecture solution, security analysis, and licensing information
        to develop a comprehensive implementation plan. You must:
        
        1. Analyze the architecture solution to understand the components and integration points
        2. Consider security concerns and how they should be addressed during implementation
        3. Factor in licensing requirements and constraints
        4. Create a detailed implementation plan with clear steps, dependencies, and estimated efforts
        5. Identify critical path items and overall timeline
        6. Highlight resources required and potential risk factors
        
        Your output should be a structured JSON that precisely follows the format requested.
        """
        
        # Create messages
        chat_messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=create_implementation_prompt(state))
        ]
        
        # Invoke model
        response = llm.invoke(chat_messages)
        
        # Parse response
        parsed_data = parse_implementation_plan(response.content)
    else:
        # For testing, create a test response
        parsed_data = {
            "implementation_plan": {
                "summary": "The implementation will take approximately 12-16 weeks in total, with a phased approach to minimize disruption.",
                "steps": [
                    {
                        "order": 1,
                        "title": "Project Initiation and Planning",
                        "description": "Define project scope, timeline, and resource requirements. Establish project team and communication channels.",
                        "estimated_effort": "2 weeks",
                        "dependencies": [0],
                        "resources_required": ["Project Manager", "IT Team Lead"],
                        "risk_factors": ["Scope creep", "Resource availability"]
                    },
                    {
                        "order": 2,
                        "title": "Environment Assessment and Preparation",
                        "description": "Inventory current file shares, assess network capacity, and prepare identity infrastructure in Azure AD.",
                        "estimated_effort": "3 weeks",
                        "dependencies": [1],
                        "resources_required": ["System Administrator", "Network Engineer"],
                        "risk_factors": ["Incomplete inventory", "Network limitations"]
                    },
                    {
                        "order": 3,
                        "title": "Security Configuration",
                        "description": "Configure security settings based on analysis.",
                        "estimated_effort": "2 weeks",
                        "dependencies": [2],
                        "resources_required": ["Security Specialist", "System Administrator"],
                        "risk_factors": ["Misconfiguration", "Policy gaps"]
                    }
                ],
                "timeline_estimate": "12-16 weeks total",
                "critical_path": ["Project Initiation and Planning", "Environment Assessment and Preparation", "Security Configuration"]
            }
        }
    
    # Update state with implementation plan
    if "implementation_plan" in parsed_data:
        plan_data = parsed_data["implementation_plan"]
        
        # Create implementation steps
        steps = create_implementation_steps(plan_data.get("steps", []))
        
        # Create implementation plan
        implementation_plan = ImplementationPlan(
            summary=plan_data.get("summary", "No summary provided"),
            steps=steps,
            timeline_estimate=plan_data.get("timeline_estimate", "Unknown"),
            critical_path=plan_data.get("critical_path", [])
        )
        
        # Update state with the implementation plan
        state.implementation_plan = implementation_plan
        
        # Also update legacy implementation fields for backward compatibility
        state.implementation_steps = steps
        state.implementation_summary = plan_data.get("summary", "No summary provided")
    
    # Update current phase
    state.current_phase = "implementation_complete"
    if "implementation" not in state.completed_phases:
        state.completed_phases.append("implementation")
    
    return state 