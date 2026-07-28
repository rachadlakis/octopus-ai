"""Start all specialist A2A agents for octopus-ai in separate processes.

Run from project root:
    python run_all_agents.py
"""

from __future__ import annotations

import signal
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

AGENT_COMMANDS = [
    ["uvicorn", "document_service_agent.document_service_agent:a2a_app", "--host", "localhost", "--port", "8101"],
    ["uvicorn", "planning_pipeline_agent.planning_pipeline_agent:a2a_app", "--host", "localhost", "--port", "8102"],
    ["uvicorn", "risk_monitor_agent.risk_monitor_agent:a2a_app", "--host", "localhost", "--port", "8103"],
    ["uvicorn", "reporting_agent.reporting_agent:a2a_app", "--host", "localhost", "--port", "8104"],
    ["uvicorn", "registry_agent.registry_agent:a2a_app", "--host", "localhost", "--port", "8105"],
]


def main() -> None:
    processes: list[subprocess.Popen] = []
    try:
        for cmd in AGENT_COMMANDS:
            proc = subprocess.Popen(cmd, cwd=ROOT)
            processes.append(proc)
            print(f"Started: {' '.join(cmd)} (pid={proc.pid})")

        print("\nAll specialist agents started.")
        print("Now run orchestrator UI in another terminal:")
        print("  adk web .")
        print("Then open http://localhost:8000 and select orchestrator_agent.")

        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\nStopping all agents...")
    finally:
        for proc in processes:
            if proc.poll() is None:
                if sys.platform == "win32":
                    proc.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    proc.terminate()


if __name__ == "__main__":
    main()
