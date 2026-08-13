# Company agents
from .developer_agent import developer_agent
from .marketing_agent import marketing_agent
from .hr_agent import hr_agent
from .testing_agent import testing_agent
from .orchestrator import ceo_agent, orchestrator

__all__ = [
    # Company roles
    "ceo_agent",
    "developer_agent",
    "marketing_agent",
    "hr_agent",
    "testing_agent",
    # Backwards compatibility
    "orchestrator",
]
