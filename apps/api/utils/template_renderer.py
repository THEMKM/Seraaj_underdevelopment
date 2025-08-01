"""
Template rendering utilities for notifications and other dynamic content
"""

import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def render_notification_template(template: str, variables: Dict[str, Any]) -> str:
    """
    Render a notification template with provided variables

    Supports simple variable substitution using {variable_name} syntax
    """

    try:
        if not template:
            return ""

        # Simple variable substitution
        rendered = template

        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            rendered = rendered.replace(placeholder, str(value))

        # Remove any remaining placeholders that weren't filled
        rendered = re.sub(r"\{[^}]+\}", "", rendered)

        # Clean up extra whitespace
        rendered = re.sub(r"\s+", " ", rendered).strip()

        return rendered

    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return template  # Return original template if rendering fails


def validate_template_variables(
    template: str, available_variables: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate that all variables in a template are available

    Returns a dict with validation results
    """

    try:
        # Find all variables in template
        variables_in_template = re.findall(r"\{([^}]+)\}", template)

        missing_variables = []
        for var in variables_in_template:
            if var not in available_variables:
                missing_variables.append(var)

        return {
            "valid": len(missing_variables) == 0,
            "variables_found": variables_in_template,
            "missing_variables": missing_variables,
            "available_variables": list(available_variables.keys()),
        }

    except Exception as e:
        logger.error(f"Error validating template variables: {e}")
        return {"valid": False, "error": str(e)}


def get_template_variables(template: str) -> List[str]:
    """Extract all variable names from a template"""

    try:
        return re.findall(r"\{([^}]+)\}", template)
    except Exception as e:
        logger.error(f"Error extracting template variables: {e}")
        return []


def preview_rendered_template(
    template: str, variables: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Preview how a template will render with given variables

    Returns both the rendered result and validation info
    """

    validation = validate_template_variables(template, variables)
    rendered = render_notification_template(template, variables)

    return {
        "original_template": template,
        "rendered_template": rendered,
        "validation": validation,
        "variables_used": variables,
    }
