"""
AI Company - Main Entry Point

Run individual agents or the CEO (orchestrator).
"""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="AI Company Agent Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py ceo         # Start the CEO (coordinates all departments)
  python main.py developer   # Start the Developer agent only
  python main.py marketing   # Start the Marketing agent only
  python main.py hr          # Start the HR agent only
  python main.py testing     # Start the Testing/QA agent only
"""
    )
    parser.add_argument(
        "agent",
        choices=["ceo", "developer", "marketing", "hr", "testing", "all"],
        default="ceo",
        nargs="?",
        help="Which agent to run (default: ceo)"
    )

    args = parser.parse_args()

    if args.agent == "ceo":
        from server import run_ceo
        print("🏢 Starting AI Company CEO on port 9000...")
        print("   Coordinating: Developer, Marketing, HR")
        run_ceo()

    elif args.agent == "developer":
        from server import run_developer_agent
        print("💻 Starting Developer Agent on port 9001...")
        run_developer_agent()

    elif args.agent == "marketing":
        from server import run_marketing_agent
        print("📢 Starting Marketing Agent on port 9002...")
        run_marketing_agent()

    elif args.agent == "hr":
        from server import run_hr_agent
        print("👥 Starting HR Agent on port 9003...")
        run_hr_agent()

    elif args.agent == "testing":
        from server import run_testing_agent
        print("🧪 Starting Testing Agent on port 9004...")
        run_testing_agent()

    elif args.agent == "all":
        print("To run all agents, start each in a separate terminal:\n")
        print("  python main.py ceo         # Port 9000 - CEO (orchestrator)")
        print("  python main.py developer   # Port 9001 - Software Development")
        print("  python main.py marketing   # Port 9002 - Marketing & Content")
        print("  python main.py hr          # Port 9003 - Human Resources")
        print("  python main.py testing     # Port 9004 - Testing & QA")
        print("\nOr just run the CEO which can delegate to all departments:")
        print("  python main.py ceo")
        sys.exit(0)


if __name__ == "__main__":
    main()
