"""Registry agent: lightweight JSON registry management exposed via A2A."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from a2a.types import AgentCapabilities, AgentCard, AgentSkill


load_dotenv()

PORT = int(os.getenv("REGISTRY_AGENT_PORT", 8105))
HOST = os.getenv("REGISTRY_AGENT_HOST", "localhost")
MODEL = "anthropic/claude-sonnet-4-5-20250929"

if not os.getenv("ANTHROPIC_API_KEY"):
    raise RuntimeError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")

WORKSPACE = Path(os.getenv("AGENT_WORKSPACE", "./workspace")).resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)
REGISTRY_FILE = WORKSPACE / "registry_records.json"


def _load_registry() -> list[dict]:
    if not REGISTRY_FILE.exists():
        return []
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _save_registry(records: list[dict]) -> None:
    REGISTRY_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")


def add_record(entity_type: str, name: str, metadata: dict | None = None) -> dict:
    """Add a typed record to local registry storage."""
    metadata = metadata or {}
    records = _load_registry()
    new_id = len(records) + 1
    record = {
        "id": new_id,
        "entity_type": entity_type,
        "name": name,
        "metadata": metadata,
    }
    records.append(record)
    _save_registry(records)
    return {"status": "success", "record": record}


def list_records(entity_type: str | None = None) -> dict:
    """List all records, optionally filtered by entity_type."""
    records = _load_registry()
    if entity_type:
        records = [r for r in records if r.get("entity_type") == entity_type]
    return {"status": "success", "count": len(records), "records": records}


def search_records(query: str) -> dict:
    """Search records by name or metadata values."""
    q = query.lower().strip()
    records = _load_registry()
    matches = []
    for record in records:
        haystack = f"{record.get('name', '')} {json.dumps(record.get('metadata', {}))}".lower()
        if q in haystack:
            matches.append(record)
    return {"status": "success", "count": len(matches), "records": matches}


root_agent = Agent(
    name="registry_agent",
    model=LiteLlm(model=MODEL),
    description="Stores and retrieves structured records in a local JSON registry.",
    instruction=(
        "Use registry tools to add, list, and search operational entities such as "
        "drivers, vehicles, routes, policies, or tasks."
    ),
    tools=[add_record, list_records, search_records],
)

skill = AgentSkill(
    id="registry",
    name="Registry",
    description="Local entity registry for operational data.",
    tags=["registry", "json", "records"],
)

agent_card = AgentCard(
    name="RegistryAgent",
    description="Local JSON registry manager agent.",
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
