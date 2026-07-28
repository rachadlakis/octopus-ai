"""Octopus orchestrator: controls all specialist agents through A2A AgentTools."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.agent_tool import AgentTool


load_dotenv()

MODEL = "anthropic/claude-sonnet-4-5-20250929"
if not os.getenv("ANTHROPIC_API_KEY"):
    raise RuntimeError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")


document_service_remote = RemoteA2aAgent(
    name="document_service_remote",
    description="Sandboxed file operations agent.",
    agent_card="http://localhost:8101/.well-known/agent-card.json",
)

planning_pipeline_remote = RemoteA2aAgent(
    name="planning_pipeline_remote",
    description="Sequential planning pipeline agent.",
    agent_card="http://localhost:8102/.well-known/agent-card.json",
)

risk_monitor_remote = RemoteA2aAgent(
    name="risk_monitor_remote",
    description="Loop-based risk monitoring refinement agent.",
    agent_card="http://localhost:8103/.well-known/agent-card.json",
)

reporting_remote = RemoteA2aAgent(
    name="reporting_remote",
    description="Structured markdown report generator.",
    agent_card="http://localhost:8104/.well-known/agent-card.json",
)

registry_remote = RemoteA2aAgent(
    name="registry_remote",
    description="Local JSON registry management agent.",
    agent_card="http://localhost:8105/.well-known/agent-card.json",
)


root_agent = Agent(
    name="orchestrator_agent",
    model=LiteLlm(model=MODEL),
    description="Orchestrates five specialist A2A agents for planning and operations workflows.",
    instruction="""
You are the Octopus orchestrator and must control all specialist agents through tools.

Specialist tools available to you:
1. document_service_remote: workspace file operations.
2. planning_pipeline_remote: sequential planning agent.
3. risk_monitor_remote: loop-based monitoring/risk agent.
4. reporting_remote: report generation.
5. registry_remote: structured record registry.

Behavior rules:
- For multi-step requests, call tools in sequence inside one turn.
- Prefer raw structured data handoff between tools when possible.
- If the user asks for planning + monitoring + report, run planner then monitor then reporter.
- Save final artifacts with document_service_remote only when the user asks to save.
""",
    tools=[
        AgentTool(agent=document_service_remote),
        AgentTool(agent=planning_pipeline_remote),
        AgentTool(agent=risk_monitor_remote),
        AgentTool(agent=reporting_remote),
        AgentTool(agent=registry_remote),
    ],
)
