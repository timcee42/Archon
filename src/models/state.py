"""
State models for the EUC Assessment Agent team.

This module defines the Pydantic models that represent the state shared between agents.
These models provide structured data representation with validation rules.
"""

from enum import Enum
from typing import Dict, List, Optional, Union, Any, Set
from datetime import datetime

from pydantic import BaseModel, Field, validator, root_validator, field_validator, model_validator, ConfigDict


class RequirementPriority(str, Enum):
    """Priority levels for requirements."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Requirement(BaseModel):
    """A specific requirement for the EUC assessment."""

    description: str = Field(..., description="Description of the requirement")
    priority: RequirementPriority = Field(
        RequirementPriority.MEDIUM, description="Priority of the requirement"
    )
    notes: Optional[str] = Field(None, description="Additional notes or context")

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        """Validate that the description is not empty."""
        if not v.strip():
            raise ValueError("Requirement description cannot be empty")
        return v


class OrganizationContext(BaseModel):
    """Organization-specific context for the assessment."""

    company_size: Optional[str] = Field(None, description="Size of the organization")
    industry: Optional[str] = Field(None, description="Industry of the organization")
    current_tech_stack: Optional[List[str]] = Field(
        None, description="Current technology stack"
    )
    compliance_requirements: Optional[List[str]] = Field(
        None, description="Compliance requirements"
    )
    additional_context: Optional[str] = Field(
        None, description="Additional context information"
    )

    @field_validator("industry")
    @classmethod
    def industry_valid(cls, v: Optional[str]) -> Optional[str]:
        """Validate that the industry is valid if provided."""
        if v is not None and not v.strip():
            raise ValueError("Industry cannot be empty if provided")
        return v


class ResearchFinding(BaseModel):
    """A research finding from the Research agent."""

    topic: str = Field(..., description="Topic of the research finding")
    content: str = Field(..., description="Content of the research finding")
    sources: List[str] = Field(default_factory=list, description="Sources of information")
    relevance: Optional[str] = Field(
        None, description="Relevance to the assessment request"
    )

    @field_validator("topic", "content")
    @classmethod
    def text_not_empty(cls, v: str, info: Any) -> str:
        """Validate that text fields are not empty."""
        if not v.strip():
            raise ValueError(f"Text field '{info.field_name}' cannot be empty")
        return v


class SecurityConcern(BaseModel):
    """A security concern identified by the Security Analyst agent."""

    description: str = Field(..., description="Description of the security concern")
    severity: str = Field(..., description="Severity of the concern (high, medium, low)")
    mitigation: Optional[str] = Field(
        None, description="Potential mitigation strategies"
    )

    @field_validator("severity")
    @classmethod
    def severity_valid(cls, v: str) -> str:
        """Validate the severity level."""
        valid_values = {"high", "medium", "low"}
        if v.lower() not in valid_values:
            raise ValueError(f"Severity must be one of: {', '.join(valid_values)}")
        return v.lower()


class LicensingInfo(BaseModel):
    """Licensing information identified by the Licensing Specialist agent."""

    model: str = Field(..., description="Licensing model")
    costs: Optional[str] = Field(None, description="Licensing costs")
    constraints: Optional[str] = Field(None, description="Licensing constraints")
    recommendations: Optional[str] = Field(
        None, description="Licensing recommendations"
    )


class ImplementationStep(BaseModel):
    """An implementation step proposed by the Implementation Engineer agent."""

    order: int = Field(..., description="Order of the step")
    title: str = Field(..., description="Title of the step")
    description: str = Field(..., description="Description of the step")
    estimated_effort: Optional[str] = Field(
        None, description="Estimated effort for this step"
    )
    dependencies: Optional[List[int]] = Field(
        None, description="Dependencies on other steps by order"
    )
    resources_required: Optional[List[str]] = Field(
        default_factory=list, description="Resources required for this implementation step"
    )
    risk_factors: Optional[List[str]] = Field(
        default_factory=list, description="Risk factors for this implementation step"
    )

    @field_validator("order")
    @classmethod
    def order_positive(cls, v: int) -> int:
        """Validate that the order is positive."""
        if v <= 0:
            raise ValueError("Implementation step order must be positive")
        return v

    @field_validator("dependencies")
    @classmethod
    def valid_dependencies(cls, v: Optional[List[int]], info: Any) -> Optional[List[int]]:
        """Validate that dependencies don't include the step itself."""
        if v is not None and "order" in info.data and info.data["order"] in v:
            raise ValueError("Implementation step cannot depend on itself")
        return v


class CostEstimate(BaseModel):
    """Cost estimate from the Cost & Value Analyst agent."""

    category: str = Field(..., description="Cost category")
    amount: Optional[float] = Field(None, description="Estimated amount")
    description: str = Field(..., description="Description of the cost")
    timeframe: Optional[str] = Field(None, description="Timeframe for the cost")

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Optional[float]) -> Optional[float]:
        """Validate that the amount is positive if provided."""
        if v is not None and v < 0:
            raise ValueError("Cost amount cannot be negative")
        return v


class SupportRequirement(BaseModel):
    """A support requirement identified by the Support & Operations agent."""
    category: Optional[str] = Field(None, description="Category of the requirement")
    description: str = Field(..., description="Description of the requirement")
    priority: Optional[str] = Field(None, description="Priority level (e.g., high, medium, low)")
    resources_needed: Optional[List[str]] = Field(
        None, description="Resources needed for support"
    )
    training_requirements: Optional[List[str]] = Field(None, description="Training requirements")
    ongoing_effort: Optional[str] = Field(
        None, description="Estimated ongoing effort"
    )


class OperationalImpact(BaseModel):
    """An operational impact identified by the Support & Operations agent."""

    area: str = Field(..., description="Affected operational area")
    description: str = Field(..., description="Description of the impact")
    severity: str = Field(..., description="Severity of the impact")
    mitigation_strategy: Optional[str] = Field(
        None, description="Strategy to mitigate the impact"
    )

    @field_validator("severity")
    @classmethod
    def severity_valid(cls, v: str) -> str:
        """Validate the severity level."""
        valid_values = {"high", "medium", "low"}
        if v.lower() not in valid_values:
            raise ValueError(f"Severity must be one of: {', '.join(valid_values)}")
        return v.lower()


class MaintenanceTask(BaseModel):
    """A maintenance task identified by the Support & Operations agent."""

    task: str = Field(..., description="Description of the task")
    frequency: str = Field(..., description="Frequency of the task")
    complexity: Optional[str] = Field(None, description="Complexity of the task (e.g., low, medium, high)")
    estimated_effort: Optional[str] = Field(
        None, description="Estimated effort for the task"
    )
    required_skills: Optional[List[str]] = Field(
        default_factory=list, description="Skills required for the task"
    )
    resources_required: Optional[List[str]] = Field(None, description="Resources required for the task")


class UserImpact(BaseModel):
    """User impact assessment from the User Experience & Enablement agent."""

    user_group: str = Field(..., description="Affected user group")
    impact_description: str = Field(..., description="Description of the impact")
    training_needs: Optional[str] = Field(None, description="Training needs")
    change_management: Optional[str] = Field(
        None, description="Change management recommendations"
    )


class TrainingNeed(BaseModel):
    """Training need identified by the User Experience & Enablement agent."""

    topic: str = Field(..., description="Topic of the training")
    description: str = Field(..., description="Description of the training")
    target_audience: List[str] = Field(..., description="Target audience for the training")
    delivery_method: str = Field(..., description="Method of delivering the training")
    duration: str = Field(..., description="Duration of the training")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites for the training")

    @field_validator("target_audience")
    @classmethod
    def audience_not_empty(cls, v: List[str]) -> List[str]:
        """Validate that the target audience is not empty."""
        if not v:
            raise ValueError("Target audience cannot be empty")
        return v


class AdoptionPhase(BaseModel):
    """A phase in the adoption plan."""

    phase: str = Field(..., description="Name of the phase")
    description: str = Field(..., description="Description of the phase")
    timeline: str = Field(..., description="Timeline for the phase")
    activities: List[str] = Field(..., description="Activities in this phase")
    success_metrics: List[str] = Field(..., description="Success metrics for this phase")

    @field_validator("activities", "success_metrics")
    @classmethod
    def list_not_empty(cls, v: List[str], info: Any) -> List[str]:
        """Validate that lists are not empty."""
        if not v:
            raise ValueError(f"{info.field_name.capitalize()} cannot be empty")
        return v


class AdoptionPlan(BaseModel):
    """Adoption plan from the User Experience & Enablement agent."""

    phases: List[AdoptionPhase] = Field(..., description="Phases in the adoption plan")
    communication_strategy: str = Field(..., description="Communication strategy")
    feedback_mechanisms: List[str] = Field(..., description="Feedback mechanisms")

    @field_validator("phases")
    @classmethod
    def phases_not_empty(cls, v: List[AdoptionPhase]) -> List[AdoptionPhase]:
        """Validate that the phases list is not empty."""
        if not v:
            raise ValueError("Adoption plan must have at least one phase")
        return v

    @field_validator("feedback_mechanisms")
    def feedback_not_empty(cls, v):
        """Validate that the feedback mechanisms list is not empty."""
        if not v:
            raise ValueError("Feedback mechanisms cannot be empty")
        return v


class ChangeImpact(BaseModel):
    """Change impact assessment from the User Experience & Enablement agent."""

    area: str = Field(..., description="Area affected by the change")
    description: str = Field(..., description="Description of the impact")
    severity: str = Field(..., description="Severity of the impact")
    mitigation_strategy: str = Field(..., description="Strategy to mitigate the impact")

    @field_validator("severity")
    @classmethod
    def severity_valid(cls, v: str) -> str:
        """Validate the severity level."""
        valid_values = {"high", "medium", "low"}
        if v.lower() not in valid_values:
            raise ValueError(f"Severity must be one of: {', '.join(valid_values)}")
        return v.lower()


class ArchitectureComponent(BaseModel):
    """An architecture component proposed by the Solution Architect agent."""

    name: str = Field(..., description="Name of the component")
    description: str = Field(..., description="Description of the component")
    purpose: str = Field(..., description="Purpose within the solution")
    dependencies: Optional[List[str]] = Field(
        None, description="Dependencies on other components"
    )

    @field_validator("name")
    @classmethod
    def name_valid(cls, v: str) -> str:
        """Validate that the component name is valid."""
        if not v.strip():
            raise ValueError("Component name cannot be empty")
        return v


class ArchitectureSolution(BaseModel):
    """Complete architecture solution from the Solution Architect agent."""

    overview: str = Field(..., description="Overview of the solution")
    components: List[ArchitectureComponent] = Field(
        default_factory=list, description="Components of the solution"
    )
    diagram_description: Optional[str] = Field(
        None, description="Textual description of the solution diagram"
    )
    considerations: Optional[str] = Field(
        None, description="Additional architectural considerations"
    )

    @field_validator("components")
    @classmethod
    def components_unique(cls, v: List[ArchitectureComponent]) -> List[ArchitectureComponent]:
        """Validate that the component names are unique."""
        names = [comp.name for comp in v]
        if len(names) != len(set(names)):
            raise ValueError("Component names must be unique")
        return v


class RequirementsSection(BaseModel):
    """Model representing a section of requirements in the assessment."""
    title: str = Field(..., description="Title of the requirements section")
    items: List[str] = Field(default_factory=list, description="List of requirement items in this section")

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: List[str], info: Any) -> List[str]:
        """Validate that items list is not empty if title is provided."""
        if "title" in info.data and info.data["title"] and not v:
            raise ValueError(f"Requirements section '{info.data['title']}' must have at least one item")
        return v


class ResearchFindings(BaseModel):
    """Model representing research findings for the assessment."""
    summary: str = Field(..., description="Summary of research findings")
    key_points: List[str] = Field(default_factory=list, description="Key points from the research")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations based on research")

    @field_validator("key_points")
    @classmethod
    def key_points_not_empty(cls, v: List[str]) -> List[str]:
        """Validate that key points are provided."""
        if not v:
            raise ValueError("Research findings must include key points")
        return v


class LicensingOption(BaseModel):
    """Model representing a licensing option in the assessment."""
    name: str = Field(..., description="Name of the licensing option")
    description: str = Field(..., description="Description of the licensing option")
    cost_estimate: str = Field(..., description="Estimated cost of the licensing option")
    pros: List[str] = Field(default_factory=list, description="Pros of the licensing option")
    cons: List[str] = Field(default_factory=list, description="Cons of the licensing option")


class ImplementationPlan(BaseModel):
    """Model representing an implementation plan for the assessment."""
    summary: str = Field(..., description="Summary of the implementation plan")
    steps: List[ImplementationStep] = Field(
        default_factory=list, description="Steps in the implementation plan"
    )
    timeline_estimate: str = Field(..., description="Estimated timeline for the implementation")
    critical_path: List[str] = Field(
        default_factory=list, description="Critical path items in the implementation"
    )

    @field_validator("steps")
    @classmethod
    def steps_not_empty(cls, v: List[ImplementationStep]) -> List[ImplementationStep]:
        """Validate that implementation steps are provided."""
        if not v:
            raise ValueError("Implementation plan must include steps")
        return v

    @model_validator(mode='after')
    def validate_plan(self) -> 'ImplementationPlan':
        """Validate that the implementation plan is coherent."""
        if self.steps and self.critical_path:
            step_titles = [step.title for step in self.steps]
            for path_item in self.critical_path:
                if path_item not in step_titles:
                    raise ValueError(f"Critical path item '{path_item}' not found in implementation steps")
        
        return self


class AssessmentState(BaseModel):
    """The main state model shared between agents."""

    # Request Information
    assessment_request: str = Field(
        ..., description="Original assessment request from the user"
    )

    # Client Information
    client_name: Optional[str] = Field(None, description="Name of the client")
    project_name: Optional[str] = Field(None, description="Name of the project")
    assessment_date: Optional[str] = Field(None, description="Date of the assessment")
    euc_description: Optional[str] = Field(None, description="Description of the EUC")
    business_context: Optional[str] = Field(None, description="Business context of the EUC")

    # Context and Requirements
    requirements: List[Requirement] = Field(
        default_factory=list, description="List of requirements"
    )
    organization_context: OrganizationContext = Field(
        default_factory=OrganizationContext, description="Organization context"
    )
    requirements_sections: List[RequirementsSection] = Field(
        default_factory=list, description="Sections of requirements"
    )

    # Research Findings
    research_findings: List[ResearchFinding] = Field(
        default_factory=list, description="Research findings"
    )
    research_summary: Optional[str] = Field(
        None, description="Summary of research findings"
    )
    research_findings_summary: Optional[ResearchFindings] = Field(
        None, description="Structured research findings"
    )

    # Architecture Solution
    architecture_solution: Optional[ArchitectureSolution] = Field(
        None, description="Architecture solution"
    )

    # Security Analysis
    security_concerns: List[SecurityConcern] = Field(
        default_factory=list, description="Security concerns"
    )
    security_summary: Optional[str] = Field(
        None, description="Summary of security analysis"
    )

    # Licensing Analysis
    licensing_info: Optional[LicensingInfo] = Field(
        None, description="Licensing information"
    )
    licensing_options: List[LicensingOption] = Field(
        default_factory=list, description="Licensing options"
    )
    recommended_licensing: Optional[str] = Field(
        None, description="Recommended licensing option"
    )

    # Implementation Plan
    implementation_steps: List[ImplementationStep] = Field(
        default_factory=list, description="Implementation steps"
    )
    implementation_summary: Optional[str] = Field(
        None, description="Summary of the implementation plan"
    )
    implementation_plan: Optional[ImplementationPlan] = Field(
        None, description="Comprehensive implementation plan"
    )

    # Support & Operations
    support_requirements: List[SupportRequirement] = Field(
        default_factory=list, description="Support requirements"
    )
    operational_impacts: List[OperationalImpact] = Field(
        default_factory=list, description="Operational impacts"
    )
    maintenance_tasks: List[MaintenanceTask] = Field(
        default_factory=list, description="Maintenance tasks"
    )
    support_summary: Optional[str] = Field(
        None, description="Summary of support requirements"
    )

    # User Experience & Enablement
    user_impacts: List[UserImpact] = Field(
        default_factory=list, description="User impacts"
    )
    training_needs: List[TrainingNeed] = Field(
        default_factory=list, description="Training needs"
    )
    adoption_plan: Optional[AdoptionPlan] = Field(
        None, description="Adoption plan"
    )
    change_impacts: List[ChangeImpact] = Field(
        default_factory=list, description="Change impacts"
    )
    user_experience_summary: Optional[str] = Field(
        None, description="Summary of user experience and enablement"
    )

    # Cost & Value Analysis
    cost_estimates: List[CostEstimate] = Field(
        default_factory=list, description="Cost estimates"
    )
    total_cost_estimate: Optional[float] = Field(
        None, description="Total cost estimate"
    )
    roi_analysis: Optional[str] = Field(None, description="ROI analysis")

    # Final Report
    final_report: Optional[str] = Field(None, description="Final assessment report")
    final_report_data: Optional[Dict[str, Any]] = Field(
        None, description="Structured final report data"
    )

    # Workflow Control
    current_phase: str = Field(
        default="init", description="Current phase of the assessment"
    )
    completed_phases: List[str] = Field(
        default_factory=list, description="Completed phases"
    )
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    
    # Metadata
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now, description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now, description="Last update timestamp"
    )
    version: str = Field(
        default="1.0", description="State model version"
    )

    @field_validator("assessment_request")
    @classmethod
    def request_not_empty(cls, v: str) -> str:
        """Validate that the assessment request is not empty."""
        if not v.strip():
            raise ValueError("Assessment request cannot be empty")
        return v

    @field_validator("current_phase")
    @classmethod
    def phase_valid(cls, v: str) -> str:
        """Validate that the current phase is valid."""
        valid_phases = {
            "init", "research", "research_complete", "architecture", 
            "architecture_complete", "security", "security_complete", 
            "licensing", "licensing_complete", "implementation", 
            "implementation_complete", "support", "support_complete",
            "user_experience", "user_experience_complete", "cost_analysis",
            "cost_analysis_complete", "complete"
        }
        if v not in valid_phases:
            raise ValueError(f"Invalid phase: {v}")
        return v

    @model_validator(mode='after')
    def validate_state(self) -> 'AssessmentState':
        """Validate the overall state consistency."""
        # Example validation: ensure research findings exist if research phase is complete
        if "research_complete" in self.completed_phases and not self.research_findings:
            # This is just an example, add more complex validation rules as needed
            pass # Or raise ValueError("Research findings are required after research phase")
        return self

    @model_validator(mode='after')
    def update_timestamp(self) -> 'AssessmentState':
        """Update the timestamp on any state change."""
        self.updated_at = datetime.now()
        return self

    # Pydantic V2 configuration using ConfigDict
    model_config = ConfigDict(extra='ignore')

# End of AssessmentState model 