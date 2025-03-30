# State Model Documentation

## Overview

The state model is the central data structure that is shared between all specialist agents in the EUC Assessment Agent team. It uses Pydantic models to provide structured data representation with validation rules, ensuring data integrity throughout the assessment process.

## Model Structure

The state model consists of a main `AssessmentState` class that contains all the data related to an assessment, including:

- Basic information (request, client, project)
- Requirements and organizational context
- Research findings
- Architecture solution
- Security analysis
- Licensing information
- Implementation plan
- Support and operations details
- User experience and enablement information
- Cost and value analysis
- Final report data
- Workflow control (phases, errors)
- Metadata (timestamps, version)

## Key Models

### RequirementPriority

An enumeration defining priority levels for requirements:

- `HIGH`
- `MEDIUM`
- `LOW`

### Requirement

Represents a specific requirement for the EUC assessment:

- `description`: Description of the requirement (required)
- `priority`: Priority of the requirement (defaults to MEDIUM)
- `notes`: Additional notes or context (optional)

### OrganizationContext

Organization-specific context for the assessment:

- `company_size`: Size of the organization (optional)
- `industry`: Industry of the organization (optional)
- `current_tech_stack`: Current technology stack (optional list)
- `compliance_requirements`: Compliance requirements (optional list)
- `additional_context`: Additional context information (optional)

### ResearchFinding

A research finding from the Research agent:

- `topic`: Topic of the research finding (required)
- `content`: Content of the research finding (required)
- `sources`: Sources of information (optional list)
- `relevance`: Relevance to the assessment request (optional)

### SecurityConcern

A security concern identified by the Security Analyst agent:

- `description`: Description of the security concern (required)
- `severity`: Severity of the concern (high, medium, low) (required)
- `mitigation`: Potential mitigation strategies (optional)

### ImplementationStep

An implementation step proposed by the Implementation Engineer agent:

- `order`: Order of the step (required, must be positive)
- `title`: Title of the step (required)
- `description`: Description of the step (required)
- `estimated_effort`: Estimated effort for this step (optional)
- `dependencies`: Dependencies on other steps by order (optional list)
- `resources_required`: Resources required for this step (optional list)
- `risk_factors`: Risk factors for this step (optional list)

### ImplementationPlan

A comprehensive implementation plan:

- `summary`: Summary of the implementation plan (required)
- `steps`: List of implementation steps (required, non-empty)
- `timeline_estimate`: Estimated timeline for the implementation (required)
- `critical_path`: Critical path items in the implementation (optional list)

### SupportRequirement

A support requirement identified by the Support & Operations agent:

- `description`: Description of the requirement (required)
- `resources_needed`: Resources needed for support (optional)
- `ongoing_effort`: Estimated ongoing effort (optional)

### OperationalImpact

An operational impact identified by the Support & Operations agent:

- `area`: Affected operational area (required)
- `description`: Description of the impact (required)
- `severity`: Severity of the impact (high, medium, low) (required)
- `mitigation_strategy`: Strategy to mitigate the impact (optional)

### TrainingNeed

A training need identified by the User Experience & Enablement agent:

- `topic`: Topic of the training (required)
- `description`: Description of the training (required)
- `target_audience`: Target audience for the training (required list, non-empty)
- `delivery_method`: Method of delivering the training (required)
- `duration`: Duration of the training (required)
- `prerequisites`: Prerequisites for the training (optional list)

### AdoptionPlan

An adoption plan from the User Experience & Enablement agent:

- `phases`: Phases in the adoption plan (required list, non-empty)
- `communication_strategy`: Communication strategy (required)
- `feedback_mechanisms`: Feedback mechanisms (required list, non-empty)

### CostEstimate

A cost estimate from the Cost & Value Analyst agent:

- `category`: Cost category (required)
- `amount`: Estimated amount (optional, must be positive if provided)
- `description`: Description of the cost (required)
- `timeframe`: Timeframe for the cost (optional)

## Validation Rules

The state model includes various validation rules to ensure data integrity:

1. **Non-empty validation**: Ensures required text fields are not empty
2. **Type validation**: Ensures data types are correct (strings, lists, numbers)
3. **Value validation**: Validates specific values (e.g., severity must be "high", "medium", or "low")
4. **Logical validation**: Ensures logical consistency (e.g., implementation steps can't depend on themselves)
5. **Cross-field validation**: Validates relationships between fields (e.g., critical path must contain valid step titles)

## Usage Examples

### Creating an Assessment State

```python
from src.models.state import AssessmentState

# Create a new assessment state
state = AssessmentState(
    assessment_request="Evaluate migration from on-premises file servers to OneDrive",
    client_name="Acme Corp",
    project_name="File Server Migration Assessment"
)
```

### Adding Requirements

```python
from src.models.state import Requirement, RequirementPriority

# Add requirements to the state
state.requirements.append(
    Requirement(
        description="Support for sharing files externally with partners",
        priority=RequirementPriority.HIGH,
        notes="Must maintain security controls"
    )
)

state.requirements.append(
    Requirement(
        description="Seamless integration with existing Microsoft 365 apps",
        priority=RequirementPriority.MEDIUM
    )
)
```

### Adding an Architecture Solution

```python
from src.models.state import ArchitectureSolution, ArchitectureComponent

# Add an architecture solution to the state
state.architecture_solution = ArchitectureSolution(
    overview="Cloud-based file sharing solution using Microsoft OneDrive and SharePoint Online",
    components=[
        ArchitectureComponent(
            name="OneDrive",
            description="Personal file storage for users",
            purpose="Store personal documents and share with specific users"
        ),
        ArchitectureComponent(
            name="SharePoint Online",
            description="Team file storage",
            purpose="Store and collaborate on team documents",
            dependencies=["OneDrive"]
        )
    ],
    considerations="Consider bandwidth requirements and network connectivity"
)
```

### Adding an Implementation Plan

```python
from src.models.state import ImplementationPlan, ImplementationStep

# Add an implementation plan to the state
state.implementation_plan = ImplementationPlan(
    summary="Phased implementation approach for OneDrive migration",
    steps=[
        ImplementationStep(
            order=1,
            title="Assessment",
            description="Assess current file share structure and usage",
            estimated_effort="2 weeks",
            resources_required=["IT Admin", "Storage Analyst"]
        ),
        ImplementationStep(
            order=2,
            title="Pilot",
            description="Pilot migration with a small user group",
            estimated_effort="3 weeks",
            dependencies=[1],
            risk_factors=["User adoption challenges"]
        ),
        ImplementationStep(
            order=3,
            title="Full Migration",
            description="Migrate all users to OneDrive",
            estimated_effort="8 weeks",
            dependencies=[2],
            resources_required=["Migration Tools", "Support Staff"]
        )
    ],
    timeline_estimate="13 weeks",
    critical_path=["Assessment", "Pilot", "Full Migration"]
)
```

### Updating the Phase

```python
# Update the current phase
state.current_phase = "research"
state.completed_phases.append("init")

# Later in the workflow
state.current_phase = "architecture"
state.completed_phases.append("research")
```

## Working with Nested Models

The state model uses nested Pydantic models, which can be accessed and modified like any Python object:

```python
# Access nested models
architecture = state.architecture_solution
if architecture:
    components = architecture.components
    for component in components:
        print(f"Component: {component.name}")
        if component.dependencies:
            print(f"  Dependencies: {', '.join(component.dependencies)}")
```

## Serialization

The state model can be serialized to and from JSON:

```python
# Convert state to JSON
state_json = state.json(indent=2)

# Save to file
with open("assessment_state.json", "w") as f:
    f.write(state_json)

# Load from JSON
from src.models.state import AssessmentState
import json

with open("assessment_state.json", "r") as f:
    state_data = json.load(f)
    loaded_state = AssessmentState(**state_data)
```

## Timestamps and Version

The state model automatically tracks creation and update timestamps:

```python
# Check when the state was created
print(f"Created at: {state.created_at}")

# Check when the state was last updated
print(f"Updated at: {state.updated_at}")

# Check state model version
print(f"State model version: {state.version}")
```

## Validation Errors

If invalid data is provided, the state model will raise validation errors:

```python
from src.models.state import SecurityConcern
from pydantic import ValidationError

try:
    # This will raise a validation error
    concern = SecurityConcern(
        description="Data leakage risk",
        severity="critical"  # Invalid - must be high, medium, or low
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Best Practices

1. **Always validate input data**: Use try/except blocks to catch ValidationError exceptions
2. **Use the model's built-in methods**: Use .dict(), .json(), etc. for conversion
3. **Follow the model's structure**: Don't bypass the model by adding attributes directly
4. **Keep the model up to date**: Update the model when requirements change
5. **Use typed variables**: Annotate variables with the correct types for better IDE support 