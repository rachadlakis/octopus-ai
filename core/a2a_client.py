"""
A2A Client - Connect to external A2A-compliant agents.

This allows ADK agents to communicate with agents from other frameworks
(CrewAI, LangChain, AutoGen, etc.) that implement the A2A protocol.
"""
import json
import urllib.request
import urllib.error
from typing import Optional
from dataclasses import dataclass


@dataclass
class AgentCard:
    """Represents an A2A agent's capabilities."""
    name: str
    description: str
    url: str
    skills: list
    version: str = "1.0.0"
    input_modes: Optional[list] = None
    output_modes: Optional[list] = None

    @classmethod
    def from_dict(cls, data: dict) -> "AgentCard":
        return cls(
            name=data.get("name", "Unknown"),
            description=data.get("description", ""),
            url=data.get("url", ""),
            skills=data.get("skills", []),
            version=data.get("version", "1.0.0"),
            input_modes=data.get("default_input_modes", ["text"]),
            output_modes=data.get("default_output_modes", ["text"]),
        )


def discover_agent(agent_url: str) -> dict:
    """
    Discover an A2A agent by fetching its agent card.

    Args:
        agent_url: Base URL of the agent (e.g., "http://localhost:9001")

    Returns:
        dict: Agent card with capabilities, skills, and metadata
    """
    try:
        # Normalize URL
        if not agent_url.startswith("http"):
            agent_url = f"http://{agent_url}"
        agent_url = agent_url.rstrip("/")

        # Fetch agent card
        card_url = f"{agent_url}/.well-known/agent.json"
        req = urllib.request.Request(
            card_url,
            headers={"Accept": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        return {
            "success": True,
            "agent": {
                "name": data.get("name"),
                "description": data.get("description"),
                "url": agent_url,
                "skills": data.get("skills", []),
                "version": data.get("version"),
                "input_modes": data.get("default_input_modes", ["text"]),
                "output_modes": data.get("default_output_modes", ["text"]),
            }
        }

    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"success": False, "error": f"Connection failed: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_message_to_agent(
    agent_url: str,
    message: str,
    session_id: Optional[str] = None
) -> dict:
    """
    Send a message to an external A2A agent.

    Args:
        agent_url: Base URL of the agent
        message: Message to send
        session_id: Optional session ID for conversation continuity

    Returns:
        dict: Agent's response
    """
    try:
        # Normalize URL
        if not agent_url.startswith("http"):
            agent_url = f"http://{agent_url}"
        agent_url = agent_url.rstrip("/")

        # A2A message format
        payload = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "id": session_id or "1",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"text": message}]
                }
            }
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            agent_url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))

        # Extract response text
        if "result" in result:
            response_parts = result.get("result", {}).get("message", {}).get("parts", [])
            response_text = ""
            for part in response_parts:
                if "text" in part:
                    response_text += part["text"]
            return {
                "success": True,
                "response": response_text,
                "raw": result
            }
        elif "error" in result:
            return {
                "success": False,
                "error": result["error"].get("message", "Unknown error")
            }
        else:
            return {"success": True, "response": str(result), "raw": result}

    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"success": False, "error": f"Connection failed: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_agent_skills(agent_url: str) -> dict:
    """
    List the skills/capabilities of an A2A agent.

    Args:
        agent_url: Base URL of the agent

    Returns:
        dict: List of agent skills
    """
    discovery = discover_agent(agent_url)
    if not discovery["success"]:
        return discovery

    skills = discovery["agent"].get("skills", [])
    return {
        "success": True,
        "agent_name": discovery["agent"]["name"],
        "skills": [
            {
                "id": s.get("id"),
                "name": s.get("name"),
                "description": s.get("description"),
                "tags": s.get("tags", [])
            }
            for s in skills
        ]
    }


class A2AClient:
    """
    Client for interacting with A2A-compliant agents.

    Usage:
        client = A2AClient("http://localhost:9001")
        info = client.discover()
        response = client.send("Hello!")
    """

    def __init__(self, agent_url: str):
        """Initialize client with agent URL."""
        self.agent_url = agent_url.rstrip("/")
        if not self.agent_url.startswith("http"):
            self.agent_url = f"http://{self.agent_url}"
        self.agent_card = None
        self.session_id = None

    def discover(self) -> AgentCard:
        """Discover and cache agent capabilities."""
        result = discover_agent(self.agent_url)
        if result["success"]:
            self.agent_card = AgentCard.from_dict(result["agent"])
            return self.agent_card
        raise ConnectionError(result["error"])

    def send(self, message: str) -> str:
        """Send message and return response text."""
        result = send_message_to_agent(
            self.agent_url,
            message,
            self.session_id
        )
        if result["success"]:
            return result["response"]
        raise RuntimeError(result["error"])

    def get_skills(self) -> list:
        """Get list of agent skills."""
        result = list_agent_skills(self.agent_url)
        if result["success"]:
            return result["skills"]
        return []


# Tools for ADK agents to use
def connect_to_external_agent(agent_url: str) -> dict:
    """
    Connect to an external A2A agent and get its information.

    Args:
        agent_url: URL of the A2A agent (e.g., "http://localhost:9001")

    Returns:
        dict: Agent information including name, skills, and capabilities
    """
    return discover_agent(agent_url)


def call_external_agent(agent_url: str, message: str) -> dict:
    """
    Send a message to an external A2A agent and get response.

    Args:
        agent_url: URL of the A2A agent
        message: Message to send to the agent

    Returns:
        dict: Agent's response
    """
    return send_message_to_agent(agent_url, message)


def get_external_agent_skills(agent_url: str) -> dict:
    """
    Get the skills/capabilities of an external A2A agent.

    Args:
        agent_url: URL of the A2A agent

    Returns:
        dict: List of agent skills with descriptions
    """
    return list_agent_skills(agent_url)
