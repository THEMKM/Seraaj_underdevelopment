"""
DEPRECATED: This module is being replaced by models/types.py

This module is maintained for backwards compatibility but all new code should
use the central type registry in models/types.py instead.

See models/types.py for:
- Forward References
- Relationship Definitions
- Field Types
- Model Mixins
"""
from typing import List
from sqlmodel import SQLModel
from models.types import (
    UserRef, UserTourProgressRef, TourStepRef
)

# Placeholder for deprecated RelationshipModel
class RelationshipModel(SQLModel):
    """
    DEPRECATED: Placeholder for backwards compatibility.
    Relationships should now be handled through direct queries as documented in each model.
    """
    pass

# Maintaining backwards compatibility
UserProgressRef = UserTourProgressRef
UserProgressList = List[UserTourProgressRef]
TourStepList = List[TourStepRef]

# Mark as deprecated
import warnings
warnings.warn(
    "relationships.py is deprecated. Use models/types.py instead.",
    DeprecationWarning,
    stacklevel=2
)
