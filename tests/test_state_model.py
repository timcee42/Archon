"""Tests for the state model in the EUC Assessment Agent team."""

import pytest
from pydantic import ValidationError
from datetime import datetime
import time
import unittest

from src.models.state import (
    AssessmentState,
    Requirement,
    RequirementPriority,
    ResearchFinding,
    SecurityConcern,
    ImplementationStep,
    ImplementationPlan,
    ArchitectureSolution,
    ArchitectureComponent,
    AdoptionPhase,
    AdoptionPlan,
    CostEstimate,
    UserImpact,
    TrainingNeed,
    ChangeImpact,
    SupportRequirement,
    OperationalImpact,
    MaintenanceTask
)


class TestRequirement:
    """Tests for the Requirement model."""

    def test_valid_requirement(self):
        """Test that a valid requirement can be created."""
        req = Requirement(
            description="Users need to access files remotely",
            priority=RequirementPriority.MEDIUM
        )
        assert req.description == "Users need to access files remotely"
        assert req.priority == RequirementPriority.MEDIUM

    def test_empty_description(self):
        """Test that a requirement with an empty description raises a validation error."""
        with pytest.raises(ValidationError) as excinfo:
            Requirement(
                description="",
                priority=RequirementPriority.MEDIUM
            )
        assert "Requirement description cannot be empty" in str(excinfo.value)


class TestSecurityConcern(unittest.TestCase):
    """Tests for the SecurityConcern model."""

    def test_valid_security_concern(self):
        """Test that a valid security concern can be created."""
        concern = SecurityConcern(
            description="Data in transit needs encryption",
            severity="high"
        )
        self.assertEqual(concern.description, "Data in transit needs encryption")
        self.assertEqual(concern.severity, "high")

    def test_invalid_severity(self):
        """Test that a security concern with invalid severity raises a validation error."""
        with pytest.raises(ValidationError) as excinfo:
            SecurityConcern(
                description="Data leakage risk",
                severity="critical"
            )
        assert "Severity must be one of" in str(excinfo.value)
        assert "medium" in str(excinfo.value)
        assert "low" in str(excinfo.value)
        assert "high" in str(excinfo.value)


class TestImplementationStep:
    """Tests for the ImplementationStep model."""

    def test_valid_implementation_step(self):
        """Test that a valid implementation step can be created."""
        step = ImplementationStep(
            order=1,
            title="Set up OneDrive",
            description="Configure OneDrive for Business",
            duration="2 days",
            dependencies=[]
        )
        assert step.order == 1
        assert step.title == "Set up OneDrive"

    def test_negative_order(self):
        """Test that an implementation step with negative order raises a validation error."""
        with pytest.raises(ValidationError) as excinfo:
            ImplementationStep(
                order=-1,
                title="Invalid Step",
                description="This should fail"
            )
        assert "Implementation step order must be positive" in str(excinfo.value)

    def test_self_dependency(self):
        """Test that an implementation step depending on itself raises a validation error."""
        with pytest.raises(ValidationError) as excinfo:
            ImplementationStep(
                order=2,
                title="Self-dependent Step",
                description="Step that depends on itself",
                dependencies=[2]
            )
        assert "Implementation step cannot depend on itself" in str(excinfo.value)


class TestCostEstimate:
    """Tests for the CostEstimate model."""

    def test_valid_cost_estimate(self):
        """Test that a valid cost estimate can be created."""
        cost = CostEstimate(
            category="Licensing",
            amount=5000.0,
            description="Annual OneDrive licensing"
        )
        assert cost.category == "Licensing"
        assert cost.amount == 5000.0

    def test_negative_amount(self):
        """Test that a cost estimate with negative amount raises a validation error."""
        with pytest.raises(ValidationError) as excinfo:
            CostEstimate(
                category="Licensing",
                amount=-5000.0,
                description="Refund amount"
            )
        assert "Cost amount cannot be negative" in str(excinfo.value)


class TestImplementationPlan(unittest.TestCase):
    """Tests for the ImplementationPlan model."""

    def test_valid_implementation_plan(self):
        """Test that a valid implementation plan can be created."""
        step1 = ImplementationStep(
            order=1,
            title="Step 1",
            description="First step",
            duration="1 day"
        )
        step2 = ImplementationStep(
            order=2,
            title="Step 2",
            description="Second step",
            duration="2 days",
            dependencies=[1]
        )
        plan = ImplementationPlan(
            summary="Test plan",
            steps=[step1, step2],
            timeline_estimate="3 days",
            critical_path=["Step 1", "Step 2"],
            risks=["Risk 1"],
            risk_mitigation={"Risk 1": "Mitigation 1"}
        )
        self.assertEqual(plan.summary, "Test plan")
        self.assertEqual(len(plan.steps), 2)

    def test_empty_steps(self):
        """Test that an implementation plan with no steps raises a validation error."""
        with pytest.raises(ValidationError) as excinfo:
            ImplementationPlan(
                summary="Empty plan",
                steps=[],
                timeline_estimate="1 month",
                critical_path=[],
                risks=["Risk"],
                risk_mitigation={"Risk": "Mitigation"}
            )
        assert "Implementation plan must include steps" in str(excinfo.value)

    def test_invalid_critical_path(self):
        """Test that an implementation plan with invalid critical path raises a validation error."""
        step = ImplementationStep(
            order=1,
            title="Step 1",
            description="First step",
            duration="1 day"
        )
        with pytest.raises(ValidationError) as excinfo:
            ImplementationPlan(
                summary="Invalid plan",
                steps=[step],
                timeline_estimate="1 week",
                critical_path=["Step 1", "NonExistentStep"],  # NonExistentStep doesn't exist
                risks=["Risk"],
                risk_mitigation={"Risk": "Mitigation"}
            )
        assert "Critical path references non-existent step" in str(excinfo.value) or "Critical path item 'NonExistentStep' not found" in str(excinfo.value)


class TestArchitectureSolution:
    """Tests for the ArchitectureSolution model."""

    def test_valid_architecture_solution(self):
        """Test that a valid architecture solution can be created."""
        component = ArchitectureComponent(
            name="OneDrive",
            description="Cloud storage component",
            purpose="Store files in the cloud"
        )
        solution = ArchitectureSolution(
            overview="Cloud storage solution",
            components=[component],
            diagram="ASCII diagram here"
        )
        assert solution.overview == "Cloud storage solution"
        assert len(solution.components) == 1

    def test_duplicate_component_names(self):
        """Test that architecture solution with duplicate component names raises a validation error."""
        with pytest.raises(ValidationError) as excinfo:
            ArchitectureSolution(
                overview="Solution with duplicate components",
                components=[
                    ArchitectureComponent(
                        name="Storage",
                        description="File storage component",
                        purpose="Store files"
                    ),
                    ArchitectureComponent(
                        name="Storage",
                        description="Another storage component",
                        purpose="More storage"
                    )
                ]
            )
        assert "Component names must be unique" in str(excinfo.value)


class TestAdoptionPlan:
    """Tests for the AdoptionPlan model."""

    def test_valid_adoption_plan(self):
        """Test that a valid adoption plan can be created."""
        phase = AdoptionPhase(
            phase="Pilot",
            description="Pilot phase with selected users",
            timeline="2 weeks",
            activities=["Select users", "Deploy solution"],
            success_metrics=["User satisfaction > 80%"]
        )
        plan = AdoptionPlan(
            phases=[phase],
            communication_strategy="Regular updates via email",
            feedback_mechanisms=["Surveys", "Focus groups"]
        )
        assert len(plan.phases) == 1
        assert plan.communication_strategy == "Regular updates via email"

    def test_empty_phases(self):
        """Test that an adoption plan with no phases raises a validation error."""
        with pytest.raises(ValidationError) as excinfo:
            AdoptionPlan(
                phases=[],
                communication_strategy="Strategy with no phases",
                feedback_mechanisms=["Surveys"]
            )
        assert "Adoption plan must have at least one phase" in str(excinfo.value)

    def test_empty_feedback_mechanisms(self):
        """Test that an adoption plan with no feedback mechanisms raises a validation error."""
        with pytest.raises(ValidationError) as excinfo:
            AdoptionPlan(
                phases=[
                    AdoptionPhase(
                        phase="Testing",
                        description="Test phase",
                        timeline="1 week",
                        activities=["Activity"],
                        success_metrics=["Metric"]
                    )
                ],
                communication_strategy="Strategy",
                feedback_mechanisms=[]
            )
        assert "Feedback mechanisms cannot be empty" in str(excinfo.value)


class TestAssessmentState(unittest.TestCase):
    """Tests for the AssessmentState model."""

    def test_valid_assessment_state(self):
        """Test that a valid assessment state can be created."""
        state = AssessmentState(
            assessment_request="Create a plan for migrating to OneDrive"
        )
        self.assertEqual(state.assessment_request, "Create a plan for migrating to OneDrive")
        self.assertEqual(state.current_phase, "init")
        self.assertEqual(len(state.requirements), 0)

    def test_empty_assessment_request(self):
        """Test that an assessment state with empty request raises a validation error."""
        with pytest.raises(ValidationError) as excinfo:
            AssessmentState(
                assessment_request=""
            )
        assert "Assessment request cannot be empty" in str(excinfo.value)

    def test_invalid_phase(self):
        """Test that an assessment state with invalid phase raises a validation error."""
        with pytest.raises(ValidationError) as excinfo:
            AssessmentState(
                assessment_request="Valid request",
                current_phase="invalid_phase"
            )
        assert "Invalid phase: invalid_phase" in str(excinfo.value) or "Invalid assessment phase" in str(excinfo.value)

    def test_update_timestamp(self):
        """Test that the timestamp is updated when the state changes."""
        state = AssessmentState(
            assessment_request="Test request"
        )
        original_timestamp = state.updated_at
        
        # Force a short delay to ensure timestamp difference
        time.sleep(0.01)
        
        # Update state
        state_dict = state.model_dump()
        state_dict["current_phase"] = "research"
        updated_state = AssessmentState(**state_dict)
        
        self.assertNotEqual(updated_state.updated_at, original_timestamp) 