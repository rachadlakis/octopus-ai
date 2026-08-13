"""
AI Company - A2A Server

Runs ADK agents as A2A-compliant services.
"""
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from core import ADKAgentExecutor
from config import HOST, PORT


def create_agent_card(name: str, description: str, skills: list, port: int) -> AgentCard:
    """Create an A2A AgentCard for the given agent."""
    return AgentCard(
        name=name,
        description=description,
        url=f"http://{HOST}:{port}/",
        default_input_modes=["text"],
        default_output_modes=["text"],
        skills=skills,
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )


def create_a2a_server(agent, agent_card: AgentCard):
    """Create an A2A server for the given ADK agent."""
    executor = ADKAgentExecutor(agent)

    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )

    return A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )


def run_developer_agent():
    """Run the developer agent as an A2A service."""
    from agents.developer_agent import developer_agent

    skills = [
        AgentSkill(
            id="development",
            name="Software Development",
            description="Write code, debug, review, and manage git repositories",
            tags=["coding", "development", "git", "debugging"],
            examples=["Write a Python function", "Review this code", "Create a Dockerfile"],
        ),
    ]

    agent_card = create_agent_card(
        name="Developer Agent",
        description="AI Company senior software developer",
        skills=skills,
        port=9001,
    )

    server = create_a2a_server(developer_agent, agent_card)
    uvicorn.run(server.build(), host=HOST, port=9001)


def run_marketing_agent():
    """Run the marketing agent as an A2A service."""
    from agents.marketing_agent import marketing_agent

    skills = [
        AgentSkill(
            id="marketing",
            name="Marketing & Content",
            description="Create marketing content, social media posts, and SEO strategies",
            tags=["marketing", "content", "social-media", "seo"],
            examples=["Write a LinkedIn post", "Analyze this headline", "Create a content calendar"],
        ),
    ]

    agent_card = create_agent_card(
        name="Marketing Agent",
        description="AI Company marketing lead",
        skills=skills,
        port=9002,
    )

    server = create_a2a_server(marketing_agent, agent_card)
    uvicorn.run(server.build(), host=HOST, port=9002)


def run_hr_agent():
    """Run the HR agent as an A2A service."""
    from agents.hr_agent import hr_agent

    skills = [
        AgentSkill(
            id="hr",
            name="Human Resources",
            description="Handle recruitment, policies, onboarding, and HR operations",
            tags=["hr", "recruitment", "policies", "onboarding"],
            examples=["Create a job description", "Generate interview questions", "Draft PTO policy"],
        ),
    ]

    agent_card = create_agent_card(
        name="HR Agent",
        description="AI Company HR manager",
        skills=skills,
        port=9003,
    )

    server = create_a2a_server(hr_agent, agent_card)
    uvicorn.run(server.build(), host=HOST, port=9003)


def run_ceo():
    """Run the CEO (orchestrator) as the main A2A service."""
    from agents.orchestrator import ceo_agent

    skills = [
        AgentSkill(
            id="orchestrate",
            name="Executive Leadership",
            description="Coordinate all departments and handle complex multi-team tasks",
            tags=["leadership", "coordination", "strategy", "management"],
            examples=["Hire a developer and have them build X", "Launch a marketing campaign"],
        ),
    ]

    agent_card = create_agent_card(
        name="AI Company CEO",
        description="CEO coordinating Developer, Marketing, and HR departments",
        skills=skills,
        port=PORT,
    )

    server = create_a2a_server(ceo_agent, agent_card)
    uvicorn.run(server.build(), host=HOST, port=PORT)


# Backwards compatibility alias
run_orchestrator = run_ceo


if __name__ == "__main__":
    run_ceo()
