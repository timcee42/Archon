"""
Tests for the EUC Assessment specialist agent modules.

This module contains test cases for the specialist agent functions
such as the Architect, Security, and Licensing agents.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from dotenv import load_dotenv
from pydantic import ValidationError

# Load the test environment variables
load_dotenv('.env.test')

from src.models.state import (
    AssessmentState, 
    Requirement, 
    RequirementPriority,
    ResearchFinding,
    ArchitectureSolution,
    ArchitectureComponent,
    SecurityConcern,
    LicensingInfo,
    ImplementationPlan,
    ImplementationStep,
    SupportRequirement,
    OperationalImpact,
    MaintenanceTask,
    UserImpact,
    TrainingNeed,
    AdoptionPlan,
    AdoptionPhase,
    ChangeImpact,
    CostEstimate,
)
from src.agents.architect import architect_agent, ArchitectOutput
from src.agents.security import security_agent, SecurityOutput
from src.agents.licensing import licensing_agent, LicensingInfo, LicensingOutput
from src.agents.implementation import implementation_agent
from src.agents.support import support_agent, SupportOperationsOutput
from src.agents.user_experience import user_experience_agent, UserExperienceOutput
from src.agents.cost_analysis import cost_analysis_agent, CostAnalysisOutput


@pytest.fixture
def sample_state_with_research():
    """Create a sample state with requirements and research findings for testing."""
    state = AssessmentState(
        assessment_request="We need to assess the feasibility of migrating our file shares to Microsoft OneDrive."
    )
    
    # Add requirements
    state.requirements = [
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
    
    # Add research findings
    state.research_findings = [
        ResearchFinding(
            topic="OneDrive Migration Best Practices",
            content="OneDrive migrations require careful planning and execution...",
            sources=["https://docs.microsoft.com/onedrive-migration"],
            relevance="Directly addresses the migration process requirement"
        )
    ]
    
    state.research_summary = "Migration to OneDrive is feasible with proper planning..."
    
    return state


@pytest.fixture
def sample_state_with_architecture(sample_state_with_research):
    """Create a sample state with architecture solution for testing."""
    state = sample_state_with_research
    
    # Add architecture solution
    state.architecture_solution = ArchitectureSolution(
        overview="The proposed solution involves migrating file shares to OneDrive with a phased approach.",
        components=[
            ArchitectureComponent(
                name="OneDrive for Business",
                description="Cloud storage service for business users.",
                purpose="Primary storage for user files",
                dependencies=["Azure AD"]
            ),
            ArchitectureComponent(
                name="Azure AD",
                description="Identity and access management service.",
                purpose="Authentication and authorization",
                dependencies=[]
            ),
            ArchitectureComponent(
                name="Migration Tool",
                description="Tool to facilitate file migration from file servers to OneDrive.",
                purpose="Data migration",
                dependencies=["OneDrive for Business", "Azure AD"]
            )
        ],
        diagram_description="A hub-and-spoke architecture with OneDrive at the center.",
        considerations="Alternative solutions considered included SharePoint and Azure Files."
    )
    
    return state


@pytest.fixture
def sample_state_with_security_licensing(sample_state_with_architecture):
    """Create a sample state with security and licensing analysis for testing."""
    state = sample_state_with_architecture
    
    # Add security concerns
    state.security_concerns = [
        SecurityConcern(
            description="Data leakage risk through external sharing",
            severity="high",
            mitigation="Configure external sharing policies to restrict sharing outside the organization"
        ),
        SecurityConcern(
            description="Insufficient access controls",
            severity="medium",
            mitigation="Implement conditional access policies and MFA"
        )
    ]
    state.security_summary = "The OneDrive migration presents several security challenges that require proper configuration and monitoring."
    
    # Add licensing info
    state.licensing_info = LicensingInfo(
        model="Microsoft 365 E3/E5 subscription model",
        costs="Approximately $20-35 per user per month depending on the chosen plan",
        constraints="Requires Microsoft 365 subscription for all users",
        recommendations="Consider Microsoft 365 E3 for most users and E5 for users requiring advanced security features"
    )
    
    return state


@pytest.fixture
def sample_state_with_implementation(sample_state_with_security_licensing):
    """Create a sample state with implementation plan for testing."""
    state = sample_state_with_security_licensing
    
    # Add implementation plan
    state.implementation_plan = ImplementationPlan(
        summary="The implementation will take approximately 12-16 weeks in total, with a phased approach to minimize disruption.",
        steps=[
            ImplementationStep(
                order=1,
                title="Project Initiation and Planning",
                description="Define project scope, timeline, and resource requirements. Establish project team and communication channels.",
                estimated_effort="2 weeks",
                dependencies=[0],
                resources_required=["Project Manager", "IT Team Lead"],
                risk_factors=["Scope creep", "Resource availability"]
            ),
            ImplementationStep(
                order=2,
                title="Environment Assessment and Preparation",
                description="Inventory current file shares, assess network capacity, and prepare identity infrastructure in Azure AD.",
                estimated_effort="3 weeks",
                dependencies=[1],
                resources_required=["System Administrator", "Network Engineer"],
                risk_factors=["Incomplete inventory", "Network limitations"]
            )
        ],
        timeline_estimate="12-16 weeks total",
        critical_path=["Project Initiation", "Environment Assessment", "Security Configuration"]
    )
    
    return state


@patch("src.agents.architect._create_architect_chain")
@patch("src.agents.architect.ChatOpenAI")
def test_architect_agent_designing_solution(mock_chat_openai, mock_create_chain, sample_state_with_research):
    """Test the architect agent designs a solution based on requirements and research."""
    # Arrange: Create mock ArchitectureOutput
    mock_component1 = ArchitectureComponent(name="OneDrive for Business", description="Cloud storage", purpose="Files", dependencies=["Azure AD"])
    mock_component2 = ArchitectureComponent(name="Azure AD", description="Identity", purpose="Auth", dependencies=[])
    mock_solution = ArchitectureSolution(
        overview="Migrate to OneDrive",
        components=[mock_component1, mock_component2],
        diagram_description="Hub and spoke",
        considerations="SharePoint considered"
    )
    mock_output = ArchitectOutput(architecture_solution=mock_solution)
    
    # Arrange: Configure the mock chain
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_output
    mock_create_chain.return_value = mock_chain
    
    # When the architect agent is called
    result = architect_agent(sample_state_with_research)
    
    # Then it should design an architecture solution
    assert result.architecture_solution == mock_solution
    mock_create_chain.assert_called_once()
    mock_chain.invoke.assert_called_once()
    # Check input contains expected keys
    invoke_args, _ = mock_chain.invoke.call_args
    assert "assessment_request" in invoke_args[0]
    assert "requirements" in invoke_args[0]
    assert "research_findings" in invoke_args[0]
    assert "research_summary" in invoke_args[0]


@patch("src.agents.security._create_security_chain")
@patch("src.agents.security.ChatOpenAI")
def test_security_agent_analyzing_solution(mock_chat_openai, mock_create_chain, sample_state_with_architecture):
    """Test the security agent analyzes the architecture solution."""
    # Arrange: Create mock SecurityOutput
    mock_concern1 = SecurityConcern(description="Data leakage risk", severity="high", mitigation="Configure policies")
    mock_concern2 = SecurityConcern(description="Insufficient access controls", severity="medium", mitigation="Implement MFA")
    mock_output = SecurityOutput(
        security_concerns=[mock_concern1, mock_concern2],
        security_summary="Challenges require proper configuration."
    )
    
    # Arrange: Configure the mock chain
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_output
    mock_create_chain.return_value = mock_chain
    
    # When the security agent is called
    result = security_agent(sample_state_with_architecture)
    
    # Then it should identify security concerns
    assert result.security_concerns == [mock_concern1, mock_concern2]
    assert result.security_summary == mock_output.security_summary
    mock_create_chain.assert_called_once()
    mock_chain.invoke.assert_called_once()
    # Check input contains expected keys
    invoke_args, _ = mock_chain.invoke.call_args
    assert "assessment_request" in invoke_args[0]
    assert "requirements" in invoke_args[0]
    assert "organization_context" in invoke_args[0]
    assert "architecture_solution" in invoke_args[0]


@patch("src.agents.licensing._create_licensing_chain")
@patch("src.agents.licensing.ChatOpenAI")
def test_licensing_agent_analyzing_solution(mock_chat_openai, mock_create_chain, sample_state_with_architecture):
    """Test the licensing agent analyzes the architecture solution."""
    # Arrange: Create mock LicensingInfo and LicensingOutput
    mock_licensing_info = LicensingInfo(
        model="Microsoft 365 E3/E5 subscription model",
        costs="Approximately $20-35 per user per month depending on the chosen plan",
        constraints="Requires Microsoft 365 subscription for all users",
        recommendations="Consider Microsoft 365 E3 for most users and E5 for users requiring advanced security features"
    )
    mock_output = LicensingOutput(licensing_info=mock_licensing_info)

    # Arrange: Configure the mock chain
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_output
    mock_create_chain.return_value = mock_chain

    # When the licensing agent is called
    result = licensing_agent(sample_state_with_architecture)

    # Then it should provide licensing information
    assert result.licensing_info == mock_licensing_info
    mock_create_chain.assert_called_once()
    mock_chain.invoke.assert_called_once()
    # Check input contains expected keys
    invoke_args, _ = mock_chain.invoke.call_args
    assert "assessment_request" in invoke_args[0]
    assert "requirements" in invoke_args[0]
    assert "organization_context" in invoke_args[0]
    assert "architecture_solution" in invoke_args[0]


@patch("langchain_openai.ChatOpenAI")
@patch("src.config.get_settings")
def test_implementation_agent_creating_plan(mock_get_settings, mock_chat_openai, sample_state_with_security_licensing):
    """Test the implementation agent creates an implementation plan."""
    # Mock settings
    mock_settings = Mock()
    mock_settings.openai_api_key = "fake-api-key"
    mock_settings.openai_model_name = "gpt-4"
    mock_settings.agent_temperature = 0.0
    mock_get_settings.return_value = mock_settings
    
    # When the implementation agent is called with testing flag
    result = implementation_agent(sample_state_with_security_licensing, testing=True)
    
    # Then it should create an implementation plan
    assert result.implementation_plan is not None
    assert "The implementation will take approximately 12-16 weeks in total" in result.implementation_plan.summary
    assert len(result.implementation_plan.steps) == 3
    assert result.implementation_plan.steps[0].title == "Project Initiation and Planning"
    assert result.implementation_plan.steps[1].title == "Environment Assessment and Preparation"
    assert result.implementation_plan.steps[2].title == "Security Configuration"
    assert result.implementation_plan.steps[0].estimated_effort == "2 weeks"
    assert result.implementation_plan.steps[0].resources_required == ["Project Manager", "IT Team Lead"]
    assert result.implementation_plan.steps[0].risk_factors == ["Scope creep", "Resource availability"]
    assert result.implementation_plan.steps[1].estimated_effort == "3 weeks"
    assert result.implementation_plan.steps[1].resources_required == ["System Administrator", "Network Engineer"]
    assert result.implementation_plan.steps[1].risk_factors == ["Incomplete inventory", "Network limitations"]
    assert result.implementation_plan.steps[2].estimated_effort == "2 weeks"
    assert result.implementation_plan.steps[2].resources_required == ["Security Specialist", "System Administrator"]
    assert result.implementation_plan.steps[2].risk_factors == ["Misconfiguration", "Policy gaps"]
    assert result.implementation_plan.timeline_estimate == "12-16 weeks total"
    assert "Project Initiation and Planning" in result.implementation_plan.critical_path
    assert "Environment Assessment and Preparation" in result.implementation_plan.critical_path
    assert "Security Configuration" in result.implementation_plan.critical_path


@patch("src.agents.support._create_support_chain")
@patch("src.agents.support.ChatOpenAI")
def test_support_agent_creating_plan(
    mock_chat_openai, 
    mock_create_chain, 
    sample_state_with_implementation
):
    """Test the support agent creates a plan based on implementation."""
    # Arrange: Create mock data
    mock_req1 = SupportRequirement(
        category="Technical",
        description="Handle OneDrive sync issues",
        priority="high",
        resources_needed=["L2 Support"],
        training_requirements=["OneDrive Admin"]
    )
    mock_impact1 = OperationalImpact(
        area="Network",
        description="Increased bandwidth needs",
        severity="medium",
        mitigation_strategy="Monitor usage"
    )
    mock_task1 = MaintenanceTask(
        task="Review sync logs",
        frequency="daily",
        complexity="low",
        resources_required=["L1 Support"]
    )
    mock_summary = "Support plan focuses on sync and network."

    # Arrange: Create mock SupportOperationsOutput
    mock_output = SupportOperationsOutput(
        support_requirements=[mock_req1],
        operational_impacts=[mock_impact1],
        maintenance_tasks=[mock_task1],
        support_summary=mock_summary
    )

    # Arrange: Configure the mock chain
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_output
    mock_create_chain.return_value = mock_chain

    # When the support agent is called
    result = support_agent(sample_state_with_implementation)

    # Then it should create a support and operations plan
    assert result.support_requirements == [mock_req1]
    assert result.operational_impacts == [mock_impact1]
    assert result.maintenance_tasks == [mock_task1]
    assert result.support_summary == mock_summary
    
    # Verify mocks were called
    mock_create_chain.assert_called_once()
    mock_chain.invoke.assert_called_once()
    # Check input contains expected keys
    invoke_args, _ = mock_chain.invoke.call_args
    assert "assessment_request" in invoke_args[0]
    assert "implementation_plan_json" in invoke_args[0]


@pytest.fixture
def sample_state_with_implementation():
    """Create a sample state with an implementation plan."""
    state = AssessmentState(
        assessment_request="Migrate file shares to Microsoft OneDrive",
        client_name="Test Client",
        project_name="OneDrive Migration",
    )

    # Add implementation plan
    state.implementation_plan = ImplementationPlan(
        summary="Comprehensive implementation plan for OneDrive migration",
        steps=[
            ImplementationStep(
                order=1,
                title="Initial Assessment",
                description="Assess current file share structure and usage patterns",
                estimated_effort="2 weeks",
                dependencies=[],
                resources_required=["File share access", "Usage analytics"],
                risk_factors=["Data volume", "User adoption"],
            ),
            ImplementationStep(
                order=2,
                title="Migration Planning",
                description="Develop detailed migration strategy and timeline",
                estimated_effort="1 week",
                dependencies=[1],
                resources_required=["Migration tools", "Project management"],
                risk_factors=["Schedule constraints", "Resource availability"],
            ),
        ],
        timeline_estimate="3 months",
        critical_path=["Initial Assessment", "Migration Planning"],
    )

    return state


@patch("src.agents.user_experience._create_ux_chain")
@patch("src.agents.user_experience.ChatOpenAI")
def test_user_experience_agent_creating_plan(
    mock_chat_openai, 
    mock_create_chain, 
    sample_state_with_implementation
):
    """Test the user experience agent creates a plan based on implementation."""
    # Arrange: Create mock data
    mock_impact1 = UserImpact(
        user_group="End Users",
        impact_description="New workflow for file access",
        training_needs="Basic OneDrive training",
        change_management="Regular updates"
    )
    mock_training1 = TrainingNeed(
        topic="OneDrive Basics",
        description="Intro to OneDrive",
        target_audience=["End Users"],
        delivery_method="Online",
        duration="1 hour",
        prerequisites=[]
    )
    mock_adoption_phase = AdoptionPhase(
        phase="Awareness",
        description="Communicate changes",
        timeline="1 week",
        activities=["Email"],
        success_metrics=["Open rate"]
    )
    mock_adoption_plan = AdoptionPlan(
        phases=[mock_adoption_phase],
        communication_strategy="Multi-channel",
        feedback_mechanisms=["Survey"]
    )
    mock_change_impact1 = ChangeImpact(
        area="Workflow",
        description="File access changes",
        severity="medium",
        mitigation_strategy="Training"
    )
    mock_summary = "Overall positive UX expected with training."

    # Arrange: Create mock UserExperienceOutput
    mock_output = UserExperienceOutput(
        user_impacts=[mock_impact1],
        training_needs=[mock_training1],
        adoption_plan=mock_adoption_plan,
        change_impacts=[mock_change_impact1],
        user_experience_summary=mock_summary
    )

    # Arrange: Configure the mock chain
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_output
    mock_create_chain.return_value = mock_chain

    # When the user experience agent is called
    result = user_experience_agent(sample_state_with_implementation)

    # Then it should create a user experience plan
    assert result.user_impacts == [mock_impact1]
    assert result.training_needs == [mock_training1]
    assert result.adoption_plan == mock_adoption_plan
    assert result.change_impacts == [mock_change_impact1]
    assert result.user_experience_summary == mock_summary
    
    # Verify mocks were called
    mock_create_chain.assert_called_once()
    mock_chain.invoke.assert_called_once()
    # Check input contains expected keys
    invoke_args, _ = mock_chain.invoke.call_args
    assert "assessment_request" in invoke_args[0]
    assert "implementation_plan_json" in invoke_args[0]


@pytest.fixture
def sample_state_with_user_experience():
    """Create a sample state with user experience details for testing."""
    # Placeholder for the actual fixture if defined elsewhere
    state = AssessmentState(assessment_request="Test Request")
    state.implementation_plan = ImplementationPlan(
        summary="Phase 1 implementation",
        steps=[ImplementationStep(order=1, title="Plan", description="Desc", estimated_effort="1wk", dependencies=[0], resources_required=[], risk_factors=[])],
        timeline_estimate="4 weeks",
        critical_path=["Plan"]
    )
    state.licensing_info = LicensingInfo(model="M365 E3", costs="$36", constraints="Per User", recommendations="E3")
    state.support_requirements = [SupportRequirement(area="Help Desk", description="Handle L1/L2", staffing="2 FTE", tools=["Ticketing"])]
    state.training_needs = [TrainingNeed(topic="OneDrive", description="Basic usage", target_audience=["Users"], delivery_method="Online", duration="1hr", prerequisites=[])]
    return state


@patch("src.agents.cost_analysis._create_cost_chain")
@patch("src.agents.cost_analysis.ChatOpenAI")
def test_cost_analysis_agent_creating_plan(
    mock_chat_openai, 
    mock_create_chain, 
    sample_state_with_user_experience
):
    """Test the cost analysis agent creates a plan based on prior state."""
    # Arrange: Create mock data
    mock_estimate1 = CostEstimate(
        category="Licensing",
        amount=10000.00,
        description="Annual M365 E3 costs",
        timeframe="per year"
    )
    mock_estimate2 = CostEstimate(
        category="Implementation",
        amount=5000.00,
        description="One-time setup",
        timeframe="one-time"
    )
    mock_total = 15000.00
    mock_roi = "Positive ROI expected within 2 years due to productivity gains."

    # Arrange: Create mock CostAnalysisOutput
    mock_output = CostAnalysisOutput(
        cost_estimates=[mock_estimate1, mock_estimate2],
        total_cost_estimate=mock_total,
        roi_analysis=mock_roi
    )

    # Arrange: Configure the mock chain
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_output
    mock_create_chain.return_value = mock_chain

    # When the cost analysis agent is called
    result = cost_analysis_agent(sample_state_with_user_experience)

    # Then it should create a cost analysis plan
    assert result.cost_estimates == [mock_estimate1, mock_estimate2]
    assert result.total_cost_estimate == mock_total
    assert result.roi_analysis == mock_roi
    
    # Verify mocks were called
    mock_create_chain.assert_called_once()
    mock_chain.invoke.assert_called_once()
    # Check input contains expected keys
    invoke_args, _ = mock_chain.invoke.call_args
    expected_keys = [
        "assessment_request",
        "implementation_plan_json",
        "licensing_info_json",
        "support_requirements_json",
        "training_needs_json"
    ]
    for key in expected_keys:
        assert key in invoke_args[0] 