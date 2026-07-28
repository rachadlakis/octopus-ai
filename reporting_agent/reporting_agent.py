"""Reporting agent: structured report generation exposed via A2A."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from a2a.types import AgentCapabilities, AgentCard, AgentSkill


load_dotenv()

PORT = int(os.getenv("REPORTING_AGENT_PORT", 8104))
HOST = os.getenv("REPORTING_AGENT_HOST", "localhost")
MODEL = "anthropic/claude-sonnet-4-5-20250929"

if not os.getenv("ANTHROPIC_API_KEY"):
    raise RuntimeError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")


def build_markdown_report(title: str, summary: str, key_points: list[str], actions: list[str]) -> dict:
    """Build a consistent markdown report from structured inputs."""
    key_points = key_points or []
    actions = actions or []

    key_points_md = "\n".join(f"- {item}" for item in key_points)
    actions_md = "\n".join(f"- {item}" for item in actions)

    markdown = (
        f"# {title}\n\n"
        f"## Summary\n{summary}\n\n"
        f"## Key Points\n{key_points_md or '- None'}\n\n"
        f"## Recommended Actions\n{actions_md or '- None'}\n"
    )

    return {
        "status": "success",
        "title": title,
        "report_markdown": markdown,
    }


root_agent = Agent(
    name="reporting_agent",
    model=LiteLlm(model=MODEL),
    description="Creates clean stakeholder reports from structured inputs.",
    instruction=(
        "Use build_markdown_report for final outputs when user asks for a report, "
        "status update, executive summary, or action memo."
    ),
    tools=[build_markdown_report],
)

skill = AgentSkill(
    id="reporting",
    name="Reporting",
    description="Generates structured markdown reports.",
    tags=["report", "summary", "markdown"],
)

agent_card = AgentCard(
    name="ReportingAgent",
    description="Structured report generator agent.",
    url=f"http://{HOST}:{PORT}/",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[skill],
    supports_authenticated_extended_card=False,
    additional_interfaces=None,
    documentation_url=None,
    icon_url=None,
    preferred_transport="JSONRPC",
    provider=None,
    signatures=None,
)

a2a_app = to_a2a(root_agent, port=PORT, agent_card=agent_card)
