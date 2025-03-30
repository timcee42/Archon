"""
Tests for the EUC Assessment agent modules.

This module contains test cases for the individual agent functions
and their integration with the LangGraph workflow.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json # Import json for dumping the object

from langchain_core.messages import AIMessage # Import AIMessage
from pydantic import ValidationError # Import directly from Pydantic
from src.models.state import AssessmentState, Requirement, RequirementPriority, OrganizationContext, ResearchFinding
from src.agents.orchestrator import orchestrator
from src.agents.context import context_agent, ContextOutput
from src.agents.research import research_agent, ResearchOutput


@pytest.fixture
def sample_state():
    """Create a sample state for testing."""
    return AssessmentState(
        assessment_request="We need to assess the feasibility of migrating our file shares to Microsoft OneDrive."
    )


@pytest.fixture
def sample_state_with_requirements(sample_state):
    """Create a sample state with requirements for testing."""
    sample_state.requirements = [
        Requirement(
            description="Evaluate security implications of OneDrive migration",
            priority=RequirementPriority.HIGH,
            notes="Focus on data protection and compliance",
        ),
        Requirement(
            description="Analyze user experience impact",
            priority=RequirementPriority.MEDIUM,
            notes=None,
        ),
    ]
    return sample_state


def test_orchestrator_initial_state(sample_state):
    """Test the orchestrator with an initial state."""
    # When the orchestrator is called with a fresh state
    result = orchestrator(sample_state)
    
    # Then it should set the initial phase
    assert result.current_phase == "context_requirements"
    assert len(result.completed_phases) == 0


def test_orchestrator_transition_from_context_to_research(sample_state_with_requirements):
    """Test the orchestrator transitions from context to research phase."""
    # Given a state with requirements and the context phase
    state = sample_state_with_requirements
    state.current_phase = "context_requirements"
    
    # When the orchestrator is called
    result = orchestrator(state)
    
    # Then it should transition to the research phase
    assert result.current_phase == "research"
    assert "context_requirements" in result.completed_phases


# Patch the helper and ChatOpenAI (to prevent its instantiation)
@patch("src.agents.context._create_context_chain")
@patch("src.agents.context.ChatOpenAI")
def test_context_agent_extracting_requirements(mock_chat_openai, mock_create_chain, sample_state):
    """Test the context agent extracts requirements using PydanticOutputParser."""
    # Mock the chain object that the helper function would return
    mock_chain = Mock()
    mock_create_chain.return_value = mock_chain
    
    # Define the expected final output object (simulating successful parsing)
    expected_output_obj = ContextOutput(
        requirements=[
            Requirement(
                description="Evaluate data migration process to OneDrive",
                priority=RequirementPriority.HIGH,
                notes="Ensure minimal disruption to users"
            )
        ],
        organization_context=OrganizationContext(
            company_size=None,
            industry=None,
            current_tech_stack=["Windows File Servers"],
            compliance_requirements=None,
            additional_context="Migration from Windows File Servers to OneDrive"
        ),
        follow_up_questions=[
            "How many users will be affected by this migration?",
            "Are there any specific compliance requirements for data storage?"
        ]
    )
    
    # Configure the mock chain's invoke method to return the expected final object
    mock_chain.invoke.return_value = expected_output_obj
    
    # When the context agent is called
    result = context_agent(sample_state)
    
    # Then it should extract requirements and context based on the mocked chain's output
    assert len(result.requirements) == 1
    mock_create_chain.assert_called_once() # Verify the helper was called
    mock_chain.invoke.assert_called_once_with({"assessment_request": sample_state.assessment_request}) # Verify chain invoked correctly
    assert result.requirements[0].description == "Evaluate data migration process to OneDrive"
    assert result.requirements[0].priority == RequirementPriority.HIGH
    assert result.requirements[0].notes == "Ensure minimal disruption to users"
    assert result.organization_context is not None
    assert result.organization_context.current_tech_stack == ["Windows File Servers"]
    assert result.organization_context.additional_context == "Migration from Windows File Servers to OneDrive"


@patch("src.agents.research._create_research_chain")
@patch("src.agents.research.ChatOpenAI") # Patch ChatOpenAI to avoid instantiation
def test_research_agent_gathering_findings(mock_chat_openai, mock_create_chain, sample_state):
    """Test the research agent gathers findings about the assessment topic."""
    # Arrange: Create mock research output
    mock_finding = ResearchFinding(
        topic="Cloud VDI Solutions",
        content="AVD and Citrix Cloud are leading options.",
        sources=["microsoft.com", "citrix.com"],
        relevance="Directly addresses the migration requirement."
    )
    mock_output = ResearchOutput(
        research_findings=[mock_finding],
        research_summary="Cloud VDI migration is feasible."
    )
    
    # Arrange: Configure the mock chain
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_output
    mock_create_chain.return_value = mock_chain
    
    # Act: Run the research agent
    updated_state = research_agent(sample_state)
    
    # Assert: Check if the state is updated correctly
    assert updated_state.research_findings == [mock_finding] # Compare the list directly
    assert updated_state.research_summary == mock_output.research_summary
    mock_create_chain.assert_called_once()
    mock_chain.invoke.assert_called_once()
    # Ensure the input to invoke contains the expected keys from the prompt
    invoke_args, invoke_kwargs = mock_chain.invoke.call_args
    assert "assessment_request" in invoke_args[0]
    assert "requirements" in invoke_args[0]
    assert "organization_context" in invoke_args[0] 