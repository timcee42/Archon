"""
Helper utilities for the EUC Assessment Agent Team.

This module contains utility functions used across the application.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def save_json(data: Dict[str, Any], filepath: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: The data to save
        filepath: Path to the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Data successfully saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving data to {filepath}: {e}")
        return False


def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load data from a JSON file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Optional[Dict[str, Any]]: The loaded data or None if failed
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        logger.info(f"Data successfully loaded from {filepath}")
        return data
    except Exception as e:
        logger.error(f"Error loading data from {filepath}: {e}")
        return None


def format_report(state_dict: Dict[str, Any]) -> str:
    """
    Format the assessment state into a readable report.
    
    Args:
        state_dict: The assessment state as a dictionary
        
    Returns:
        str: Formatted report text
    """
    report = "# EUC Assessment Report\n\n"
    
    # Add assessment request
    report += f"## Assessment Request\n\n{state_dict.get('assessment_request', 'No request provided')}\n\n"
    
    # Add requirements
    report += "## Requirements\n\n"
    requirements = state_dict.get('requirements', [])
    if requirements:
        for i, req in enumerate(requirements, 1):
            priority = req.get('priority', 'medium').upper()
            report += f"{i}. [**{priority}**] {req.get('description', 'No description')}\n"
            if req.get('notes'):
                report += f"   - *Note: {req['notes']}*\n"
    else:
        report += "No requirements identified.\n"
    
    # Add organization context
    org_context = state_dict.get('organization_context', {})
    if any(org_context.values()):
        report += "\n## Organization Context\n\n"
        if org_context.get('company_size'):
            report += f"**Company Size:** {org_context['company_size']}\n\n"
        if org_context.get('industry'):
            report += f"**Industry:** {org_context['industry']}\n\n"
        if org_context.get('current_tech_stack'):
            report += f"**Current Technology Stack:** {', '.join(org_context['current_tech_stack'])}\n\n"
        if org_context.get('compliance_requirements'):
            report += f"**Compliance Requirements:** {', '.join(org_context['compliance_requirements'])}\n\n"
        if org_context.get('additional_context'):
            report += f"**Additional Context:** {org_context['additional_context']}\n\n"
    
    # Add research summary
    if state_dict.get('research_summary'):
        report += f"\n## Research Summary\n\n{state_dict['research_summary']}\n\n"
        
        # Add research findings
        findings = state_dict.get('research_findings', [])
        if findings:
            report += "### Research Findings\n\n"
            for i, finding in enumerate(findings, 1):
                report += f"#### {i}. {finding.get('topic', 'Untitled Topic')}\n\n"
                report += f"{finding.get('content', 'No content')}\n\n"
                if finding.get('sources'):
                    report += "**Sources:**\n"
                    for source in finding['sources']:
                        report += f"- {source}\n"
                report += "\n"
    
    # Add architecture solution
    arch_solution = state_dict.get('architecture_solution', {})
    if arch_solution:
        report += "## Architecture Solution\n\n"
        report += f"### Overview\n\n{arch_solution.get('overview', 'No overview provided')}\n\n"
        
        components = arch_solution.get('components', [])
        if components:
            report += "### Components\n\n"
            for comp in components:
                report += f"#### {comp.get('name', 'Unnamed Component')}\n\n"
                report += f"**Purpose:** {comp.get('purpose', 'No purpose specified')}\n\n"
                report += f"{comp.get('description', 'No description')}\n\n"
                if comp.get('dependencies'):
                    report += "**Dependencies:** " + ", ".join(comp['dependencies']) + "\n\n"
        
        if arch_solution.get('diagram_description'):
            report += f"### Architecture Diagram\n\n{arch_solution['diagram_description']}\n\n"
        
        if arch_solution.get('considerations'):
            report += f"### Architectural Considerations\n\n{arch_solution['considerations']}\n\n"
    
    # Add security analysis
    if state_dict.get('security_summary'):
        report += f"## Security Analysis\n\n{state_dict['security_summary']}\n\n"
        
        # Add security concerns
        concerns = state_dict.get('security_concerns', [])
        if concerns:
            report += "### Security Concerns\n\n"
            for i, concern in enumerate(concerns, 1):
                severity = concern.get('severity', 'medium').upper()
                report += f"#### {i}. {concern.get('description', 'Unnamed Concern')} [**{severity}**]\n\n"
                if concern.get('mitigation'):
                    report += f"**Mitigation:** {concern['mitigation']}\n\n"
    
    # Add licensing information
    licensing_info = state_dict.get('licensing_info', {})
    if licensing_info:
        report += "## Licensing Analysis\n\n"
        report += f"### Licensing Model\n\n{licensing_info.get('model', 'No licensing model specified')}\n\n"
        
        if licensing_info.get('costs'):
            report += f"### Licensing Costs\n\n{licensing_info['costs']}\n\n"
        
        if licensing_info.get('constraints'):
            report += f"### Licensing Constraints\n\n{licensing_info['constraints']}\n\n"
        
        if licensing_info.get('recommendations'):
            report += f"### Licensing Recommendations\n\n{licensing_info['recommendations']}\n\n"

    # Add implementation section if available
    if state_dict.get('implementation_summary'):
        report += f"## Implementation Plan\n\n{state_dict['implementation_summary']}\n\n"
        
        steps = state_dict.get('implementation_steps', [])
        if steps:
            report += "### Implementation Steps\n\n"
            # Sort steps by order
            sorted_steps = sorted(steps, key=lambda x: x.get('order', 999))
            for step in sorted_steps:
                report += f"#### Step {step.get('order', '?')}: {step.get('title', 'Unnamed Step')}\n\n"
                report += f"{step.get('description', 'No description')}\n\n"
                if step.get('estimated_effort'):
                    report += f"**Estimated Effort:** {step['estimated_effort']}\n\n"
                if step.get('dependencies'):
                    report += f"**Dependencies:** Steps {', '.join(map(str, step['dependencies']))}\n\n"
    
    # Add completed phases summary
    completed_phases = state_dict.get('completed_phases', [])
    current_phase = state_dict.get('current_phase')
    if completed_phases or current_phase:
        report += "## Assessment Progress\n\n"
        if completed_phases:
            report += f"**Completed Phases:** {', '.join(completed_phases)}\n\n"
        if current_phase:
            report += f"**Current Phase:** {current_phase}\n\n"
    
    return report 