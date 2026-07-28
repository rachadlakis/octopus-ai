"""Risk monitor agent: iterative LoopAgent for risk monitoring tasks exposed via A2A."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.tool_context import ToolContext

from a2a.types import AgentCapabilities, AgentCard, AgentSkill


load_dotenv()

PORT = int(os.getenv("RISK_MONITOR_AGENT_PORT", 8103))
HOST = os.getenv("RISK_MONITOR_AGENT_HOST", "localhost")
MODEL = "anthropic/claude-sonnet-4-5-20250929"

if not os.getenv("ANTHROPIC_API_KEY"):
    raise RuntimeError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")

STATE_REPORT = "monitor_report"
STATE_FEEDBACK = "monitor_feedback"
DONE_SENTINEL = "MONITORING_COMPLETE"


def finalize_cycle(tool_context: ToolContext) -> dict:
    """Exit the loop when quality criteria are met."""
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    return {"status": "completed"}


def initialize_state(callback_context: CallbackContext) -> None:
    callback_context.state[STATE_REPORT] = callback_context.state.get(
        STATE_REPORT,
        "Initial monitor draft: parse the request and propose a first-pass risk summary.",
    )


inspector_agent = LlmAgent(
    name="inspector_agent",
    model=LiteLlm(model=MODEL),
    include_contents="none",
    instruction=f"""
You are a risk inspector.

Current report:
{{{{{STATE_REPORT}}}}}

Task:
- Review for clarity, prioritization, and actionability.
- If the report is already strong, output exactly: {DONE_SENTINEL}
- Otherwise output precise improvement feedback in 2-5 bullets.
""",
    description="Checks report quality and emits feedback or completion signal.",
    output_key=STATE_FEEDBACK,
)

improver_agent = LlmAgent(
    name="improver_agent",
    model=LiteLlm(model=MODEL),
    include_contents="none",
    instruction=f"""
You are a risk report improver.

Current report:
{{{{{STATE_REPORT}}}}}

Feedback:
{{{{{STATE_FEEDBACK}}}}}

If feedback is exactly {DONE_SENTINEL}, call finalize_cycle and do not output text.
Otherwise return an improved report with sections: Summary, Critical Risks, Warnings, Next Actions.
""",
    description="Improves report or exits loop when complete.",
    tools=[finalize_cycle],
    output_key=STATE_REPORT,
)

root_agent = LoopAgent(
    name="risk_monitor_agent",
    description="Iterative monitor agent that refines risk reports until complete.",
    before_agent_callback=initialize_state,
    sub_agents=[inspector_agent, improver_agent],
    max_iterations=4,
)

skill = AgentSkill(
    id="risk_monitoring",
    name="Risk Monitor Loop",
    description="Iteratively improves monitoring and risk reports.",
    tags=["monitoring", "loop", "risk"],
)

agent_card = AgentCard(
    name="RiskMonitorAgent",
    description="Loop-based risk monitoring refinement agent.",
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
