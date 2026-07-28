"""Document service agent: sandboxed workspace file operations exposed via A2A."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from a2a.types import AgentCapabilities, AgentCard, AgentSkill


load_dotenv()

PORT = int(os.getenv("DOCUMENT_SERVICE_AGENT_PORT", 8101))
HOST = os.getenv("DOCUMENT_SERVICE_AGENT_HOST", "localhost")
WORKSPACE = Path(os.getenv("AGENT_WORKSPACE", "./workspace")).resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

MODEL = "anthropic/claude-sonnet-4-5-20250929"
if not os.getenv("ANTHROPIC_API_KEY"):
    raise RuntimeError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")


def _resolve(path: str) -> Path:
    candidate = (WORKSPACE / path).resolve()
    if candidate != WORKSPACE and WORKSPACE not in candidate.parents:
        raise ValueError(f"Path '{path}' escapes workspace")
    return candidate


def list_files(subdir: str = ".") -> dict:
    """List files in the sandbox workspace."""
    try:
        target = _resolve(subdir)
        if not target.is_dir():
            return {"status": "error", "error_message": f"'{subdir}' is not a directory"}
        entries = [
            {
                "name": str(p.relative_to(WORKSPACE)),
                "type": "dir" if p.is_dir() else "file",
                "size_bytes": p.stat().st_size if p.is_file() else 0,
            }
            for p in sorted(target.iterdir())
        ]
        return {"status": "success", "entries": entries}
    except (ValueError, OSError) as exc:
        return {"status": "error", "error_message": str(exc)}


def read_text(path: str) -> dict:
    """Read a UTF-8 text file from the sandbox workspace."""
    try:
        target = _resolve(path)
        if not target.is_file():
            return {"status": "error", "error_message": f"File '{path}' not found"}
        return {"status": "success", "path": path, "content": target.read_text(encoding="utf-8")}
    except (ValueError, OSError, UnicodeDecodeError) as exc:
        return {"status": "error", "error_message": str(exc)}


def write_text(path: str, content: str, mode: str = "overwrite") -> dict:
    """Write UTF-8 text in overwrite or append mode."""
    if mode not in {"overwrite", "append"}:
        return {"status": "error", "error_message": "mode must be overwrite or append"}
    try:
        target = _resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        file_mode = "w" if mode == "overwrite" else "a"
        with open(target, file_mode, encoding="utf-8") as f:
            f.write(content)
        return {"status": "success", "path": path, "bytes_written": len(content.encode("utf-8"))}
    except (ValueError, OSError) as exc:
        return {"status": "error", "error_message": str(exc)}


def delete_file(path: str) -> dict:
    """Delete a file in the sandbox workspace."""
    try:
        target = _resolve(path)
        if not target.is_file():
            return {"status": "error", "error_message": f"File '{path}' not found"}
        target.unlink()
        return {"status": "success", "path": path}
    except (ValueError, OSError) as exc:
        return {"status": "error", "error_message": str(exc)}


root_agent = Agent(
    name="document_service_agent",
    model=LiteLlm(model=MODEL),
    description="Sandboxed file management for workspace text files.",
    instruction=(
        "Use file tools for read/write/list/delete operations in the sandbox workspace. "
        "Ask before deleting files. Report tool errors plainly and stop."
    ),
    tools=[list_files, read_text, write_text, delete_file],
)

skill = AgentSkill(
    id="document_service_ops",
    name="Document Service Operations",
    description="List, read, write, and delete workspace text files.",
    tags=["file", "workspace", "text"],
)

agent_card = AgentCard(
    name="DocumentServiceAgent",
    description="Sandboxed text file operations agent.",
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
