"""
Enhanced validation utilities with better error handling
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from middleware.error_handler import DataValidationError, BusinessLogicError


def validate_email(email: str) -> str:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise DataValidationError(
            "Invalid email format",
            field="email",
            value=email
        )
    return email.lower()


def validate_password_strength(password: str) -> str:
    """Validate password strength"""
    if len(password) < 8:
        raise DataValidationError(
            "Password must be at least 8 characters long",
            field="password"
        )
    
    if not re.search(r'[A-Z]', password):
        raise DataValidationError(
            "Password must contain at least one uppercase letter",
            field="password"
        )
    
    if not re.search(r'[a-z]', password):
        raise DataValidationError(
            "Password must contain at least one lowercase letter",
            field="password"
        )
    
    if not re.search(r'\d', password):
        raise DataValidationError(
            "Password must contain at least one number",
            field="password"
        )
    
    return password


def validate_phone_number(phone: str) -> str:
    """Validate phone number format"""
    # Simple international phone number validation
    phone_pattern = r'^\+?[1-9]\d{1,14}$'
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    if not re.match(phone_pattern, cleaned_phone):
        raise DataValidationError(
            "Invalid phone number format",
            field="phone_number",
            value=phone
        )
    
    return cleaned_phone


def validate_date_range(start_date: date, end_date: date, field_prefix: str = "") -> tuple:
    """Validate that end date is after start date"""
    if start_date >= end_date:
        raise DataValidationError(
            f"End date must be after start date",
            field=f"{field_prefix}date_range"
        )
    
    # Check if dates are not too far in the past or future
    today = date.today()
    if start_date < date(today.year - 10, today.month, today.day):
        raise DataValidationError(
            "Start date cannot be more than 10 years in the past",
            field=f"{field_prefix}start_date"
        )
    
    if end_date > date(today.year + 5, today.month, today.day):
        raise DataValidationError(
            "End date cannot be more than 5 years in the future",
            field=f"{field_prefix}end_date"
        )
    
    return start_date, end_date


def validate_file_type(filename: str, allowed_types: List[str]) -> str:
    """Validate file type based on extension"""
    if not filename:
        raise DataValidationError("Filename is required", field="filename")
    
    file_extension = filename.lower().split('.')[-1]
    
    if file_extension not in allowed_types:
        raise DataValidationError(
            f"File type '{file_extension}' not allowed. Allowed types: {', '.join(allowed_types)}",
            field="file_type",
            value=file_extension
        )
    
    return file_extension


def validate_file_size(file_size: int, max_size_mb: int) -> int:
    """Validate file size"""
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        raise DataValidationError(
            f"File size exceeds maximum limit of {max_size_mb}MB",
            field="file_size",
            value=f"{file_size / 1024 / 1024:.2f}MB"
        )
    
    return file_size


def validate_skills_list(skills: List[str]) -> List[str]:
    """Validate skills list"""
    if not skills:
        raise DataValidationError("At least one skill is required", field="skills")
    
    if len(skills) > 20:
        raise DataValidationError(
            "Maximum 20 skills allowed",
            field="skills",
            value=len(skills)
        )
    
    validated_skills = []
    for skill in skills:
        if not skill or len(skill.strip()) < 2:
            raise DataValidationError(
                "Each skill must be at least 2 characters long",
                field="skills"
            )
        
        if len(skill) > 50:
            raise DataValidationError(
                "Each skill must be 50 characters or less",
                field="skills",
                value=skill
            )
        
        validated_skills.append(skill.strip().title())
    
    return list(set(validated_skills))  # Remove duplicates


def validate_url(url: str, field_name: str = "url") -> str:
    """Validate URL format"""
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    
    if not re.match(url_pattern, url):
        raise DataValidationError(
            "Invalid URL format",
            field=field_name,
            value=url
        )
    
    return url


def validate_text_length(
    text: str, 
    field_name: str,
    min_length: int = 0,
    max_length: int = 1000,
    required: bool = True
) -> str:
    """Validate text length"""
    if not text and required:
        raise DataValidationError(f"{field_name} is required", field=field_name)
    
    if not text:
        return ""
    
    text = text.strip()
    
    if len(text) < min_length:
        raise DataValidationError(
            f"{field_name} must be at least {min_length} characters long",
            field=field_name,
            value=len(text)
        )
    
    if len(text) > max_length:
        raise DataValidationError(
            f"{field_name} must be {max_length} characters or less",
            field=field_name,
            value=len(text)
        )
    
    return text


def validate_choice(value: str, choices: List[str], field_name: str) -> str:
    """Validate that value is in allowed choices"""
    if value not in choices:
        raise DataValidationError(
            f"Invalid {field_name}. Must be one of: {', '.join(choices)}",
            field=field_name,
            value=value
        )
    
    return value


def validate_numeric_range(
    value: float,
    field_name: str,
    min_value: float = None,
    max_value: float = None
) -> float:
    """Validate numeric value within range"""
    if min_value is not None and value < min_value:
        raise DataValidationError(
            f"{field_name} must be at least {min_value}",
            field=field_name,
            value=value
        )
    
    if max_value is not None and value > max_value:
        raise DataValidationError(
            f"{field_name} must be at most {max_value}",
            field=field_name,
            value=value
        )
    
    return value


def validate_opportunity_data(opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate opportunity creation/update data"""
    validated_data = {}
    
    # Required fields
    validated_data["title"] = validate_text_length(
        opportunity_data.get("title", ""), "title", min_length=5, max_length=200
    )
    
    validated_data["description"] = validate_text_length(
        opportunity_data.get("description", ""), "description", min_length=20, max_length=2000
    )
    
    # Skills validation
    if "skills_required" in opportunity_data:
        validated_data["skills_required"] = validate_skills_list(
            opportunity_data["skills_required"]
        )
    
    # Location validation
    if "location" in opportunity_data:
        validated_data["location"] = validate_text_length(
            opportunity_data["location"], "location", max_length=200
        )
    
    # Volunteers needed validation
    if "volunteers_needed" in opportunity_data:
        validated_data["volunteers_needed"] = int(validate_numeric_range(
            float(opportunity_data["volunteers_needed"]), 
            "volunteers_needed", 
            min_value=1, 
            max_value=1000
        ))
    
    # Date validation
    if "start_date" in opportunity_data and "end_date" in opportunity_data:
        start_date = datetime.fromisoformat(opportunity_data["start_date"]).date()
        end_date = datetime.fromisoformat(opportunity_data["end_date"]).date()
        validated_data["start_date"], validated_data["end_date"] = validate_date_range(
            start_date, end_date, "opportunity_"
        )
    
    # Category validation
    if "category" in opportunity_data:
        valid_categories = [
            "Education", "Health", "Environment", "Technology", "Arts", 
            "Sports", "Community", "Elderly Care", "Youth Development", "Other"
        ]
        validated_data["category"] = validate_choice(
            opportunity_data["category"], valid_categories, "category"
        )
    
    return {**opportunity_data, **validated_data}


def validate_application_data(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate application data"""
    validated_data = {}
    
    # Cover letter validation
    validated_data["cover_letter"] = validate_text_length(
        application_data.get("cover_letter", ""), 
        "cover_letter", 
        min_length=50, 
        max_length=2000
    )
    
    # Availability validation
    if "availability" in application_data:
        availability = application_data["availability"]
        
        if "hours_per_week" in availability:
            validated_data.setdefault("availability", {})["hours_per_week"] = int(
                validate_numeric_range(
                    float(availability["hours_per_week"]),
                    "hours_per_week",
                    min_value=1,
                    max_value=168  # Hours in a week
                )
            )
    
    # Experience validation
    if "relevant_experience" in application_data:
        validated_data["relevant_experience"] = validate_text_length(
            application_data["relevant_experience"],
            "relevant_experience",
            max_length=1000,
            required=False
        )
    
    return {**application_data, **validated_data}


def sanitize_html_content(content: str) -> str:
    """Basic HTML sanitization (in production, use a proper library like bleach)"""
    import html
    
    # Escape HTML characters
    sanitized = html.escape(content)
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r'<script.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'onclick='
    ]
    
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized


# Validation decorators
def validate_request_data(validation_func):
    """Decorator to validate request data"""
    def decorator(endpoint_func):
        async def wrapper(*args, **kwargs):
            # Find request data in kwargs
            for key, value in kwargs.items():
                if isinstance(value, dict) and key.endswith('_data'):
                    kwargs[key] = validation_func(value)
            
            return await endpoint_func(*args, **kwargs)
        return wrapper
    return decorator


class ValidationResult:
    """Result of validation with errors and warnings"""
    
    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.is_valid = True
    
    def add_error(self, field: str, message: str, value: Any = None):
        """Add validation error"""
        self.errors.append({
            "field": field,
            "message": message,
            "value": value
        })
        self.is_valid = False
    
    def add_warning(self, field: str, message: str, value: Any = None):
        """Add validation warning"""
        self.warnings.append({
            "field": field,
            "message": message,
            "value": value
        })
    
    def raise_if_invalid(self):
        """Raise exception if validation failed"""
        if not self.is_valid:
            raise DataValidationError(
                f"Validation failed with {len(self.errors)} errors",
                details={
                    "errors": self.errors,
                    "warnings": self.warnings
                }
            )