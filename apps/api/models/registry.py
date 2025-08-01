"""
Central model registry to avoid circular imports
Import this module when you need access to model types
"""
from typing import TYPE_CHECKING

# Models will be populated at runtime
__models__ = {}

if TYPE_CHECKING:
    from .user import User
    from .organisation import Organisation
    from .opportunity import Opportunity
    from .application import Application
    from .review import Review
    
    # Type hints for IDE support
    User = User
    Organisation = Organisation
    Opportunity = Opportunity
    Application = Application
    Review = Review
