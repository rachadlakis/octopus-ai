"""Planning pipeline agent: sequential planning workflow exposed via A2A."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm

from a2a.types import AgentCapabilities, AgentCard, AgentSkill


load_dotenv()

PORT = int(os.getenv("PLANNING_PIPELINE_AGENT_PORT", 8102))
HOST = os.getenv("PLANNING_PIPELINE_AGENT_HOST", "localhost")
MODEL = "anthropic/claude-sonnet-4-5-20250929"

if not os.getenv("ANTHROPIC_API_KEY"):
    raise RuntimeError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")


brief_agent = LlmAgent(
    name="brief_agent",
    model=LiteLlm(model=MODEL),
    instruction=(
        "Convert the user request into a concise project brief with goal, constraints, "
        "inputs, and expected deliverable. Output only structured bullet points."
    ),
    description="Creates a normalized planning brief.",
    output_key="planning_brief",
)

plan_agent = LlmAgent(
    name="plan_agent",
    model=LiteLlm(model=MODEL),
    instruction=(
        "Use planning_brief to create a practical execution plan with phases, tasks, "
        "dependencies, and owner role suggestions. Output markdown."
    ),
    description="Generates a step-by-step plan.",
    output_key="draft_plan",
)

qa_agent = LlmAgent(
    name="qa_agent",
    model=LiteLlm(model=MODEL),
    instruction=(
        "Validate draft_plan for missing steps and unrealistic sequencing. "
        "Return a polished final plan with a short risk checklist."
    ),
    description="Performs quality pass over plan.",
    output_key="final_plan",
)

root_agent = SequentialAgent(
    name="planning_pipeline_agent",
    description="Sequential planning specialist for project and operations plans.",
    sub_agents=[brief_agent, plan_agent, qa_agent],
)

skill = AgentSkill(
    id="planning_pipeline",
    name="Planning Pipeline",
    description="Transforms vague requests into validated execution plans.",
    tags=["planning", "sequential", "workflow"],
)

agent_card = AgentCard(
    name="PlanningPipelineAgent",
    description="Sequential planning pipeline agent.",
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
