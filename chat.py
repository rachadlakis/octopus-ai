"""
AI Company - Terminal Chat Interface

A simple terminal-based chat for interacting with agents.
Usage: python chat.py [agent_name]
"""
import argparse
import asyncio
import sys
import os

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


AGENTS = {
    "ceo": ("🏢", "CEO - Coordinates all departments"),
    "developer": ("💻", "Developer - Code, Git, GitHub"),
    "marketing": ("📢", "Marketing - Content, Social, SEO"),
    "hr": ("👥", "HR - Recruitment, Policies"),
    "testing": ("🧪", "Testing - QA, Coverage, Quality"),
}


def get_agent(agent_key: str):
    """Import and return the selected agent."""
    if agent_key == "ceo":
        from agents.orchestrator import ceo_agent
        return ceo_agent
    elif agent_key == "developer":
        from agents.developer_agent import developer_agent
        return developer_agent
    elif agent_key == "marketing":
        from agents.marketing_agent import marketing_agent
        return marketing_agent
    elif agent_key == "hr":
        from agents.hr_agent import hr_agent
        return hr_agent
    elif agent_key == "testing":
        from agents.testing_agent import testing_agent
        return testing_agent
    return None


async def chat_loop(agent, agent_name: str, icon: str):
    """Main chat loop."""
    session_service = InMemorySessionService()

    runner = Runner(
        agent=agent,
        app_name=agent.name,
        session_service=session_service,
    )

    # Create session
    session = session_service.create_session(
        app_name=agent.name,
        user_id="terminal_user",
        session_id="terminal_session",
        state={}
    )

    print(f"\n{icon} Chat with {agent_name}")
    print("=" * 50)
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n👤 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print(f"\n{icon} Goodbye!")
                break

            if user_input.lower() == "clear":
                session = session_service.create_session(
                    app_name=agent.name,
                    user_id="terminal_user",
                    session_id=f"terminal_session_{id(session)}",
                    state={}
                )
                print("\n🗑️ Conversation cleared.")
                continue

            # Get response
            print(f"\n{icon} {agent_name}: ", end="", flush=True)

            response_text = ""
            async for event in runner.run(
                user_id="terminal_user",
                session_id=session.id,
                new_message=user_input
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            # Stream-like output
                            print(part.text, end="", flush=True)
                            response_text += part.text

            if not response_text:
                print("(No response)")

            print()  # New line after response

        except KeyboardInterrupt:
            print(f"\n\n{icon} Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="AI Company Terminal Chat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chat.py ceo         # Chat with the CEO
  python chat.py developer   # Chat with the Developer
  python chat.py marketing   # Chat with Marketing
  python chat.py hr          # Chat with HR
  python chat.py testing     # Chat with Testing/QA
"""
    )
    parser.add_argument(
        "agent",
        choices=list(AGENTS.keys()),
        default="ceo",
        nargs="?",
        help="Which agent to chat with (default: ceo)"
    )

    args = parser.parse_args()

    icon, description = AGENTS[args.agent]

    print("\n" + "=" * 50)
    print(f"  🏢 AI COMPANY - {args.agent.upper()}")
    print(f"  {description}")
    print("=" * 50)

    agent = get_agent(args.agent)
    if not agent:
        print(f"❌ Error: Could not load agent '{args.agent}'")
        sys.exit(1)

    # Run chat loop
    asyncio.run(chat_loop(agent, args.agent.upper(), icon))


if __name__ == "__main__":
    main()
