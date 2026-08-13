"""
AI Company - ADK Web UI Runner

Run agents using ADK's built-in web interface.
Usage: python run_adk_ui.py [agent_name]
"""
import argparse
import subprocess
import sys
import os

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description="Run AI Company agents with ADK Web UI")
    parser.add_argument(
        "agent",
        choices=["ceo", "developer", "marketing", "hr", "testing"],
        default="ceo",
        nargs="?",
        help="Which agent to run (default: ceo)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the web UI (default: 8000)"
    )

    args = parser.parse_args()

    # Map agent names to module paths
    agent_modules = {
        "ceo": "agents.orchestrator:ceo_agent",
        "developer": "agents.developer_agent:developer_agent",
        "marketing": "agents.marketing_agent:marketing_agent",
        "hr": "agents.hr_agent:hr_agent",
        "testing": "agents.testing_agent:testing_agent",
    }

    agent_path = agent_modules[args.agent]

    print(f"🏢 Starting AI Company - {args.agent.upper()} Agent")
    print(f"🌐 Web UI will be available at: http://localhost:{args.port}")
    print(f"📦 Agent: {agent_path}")
    print("-" * 50)

    # Run ADK web command
    try:
        subprocess.run([
            "adk", "web",
            "--agent", agent_path,
            "--port", str(args.port)
        ], check=True)
    except FileNotFoundError:
        print("\n❌ Error: 'adk' command not found.")
        print("   Make sure google-adk is installed: pip install google-adk")
        print("\n   Alternatively, run the Streamlit UI:")
        print("   streamlit run ui.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")


if __name__ == "__main__":
    main()
