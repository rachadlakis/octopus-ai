"""
Developer Agent - Software development, code review, and technical tasks.

This agent is the company's technical expert handling all coding,
debugging, and development operations.

Supports MCP tools for GitHub integration when GITHUB_TOKEN is set.
"""
import os
import asyncio
from typing import Any
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

from config import DEFAULT_MODEL
from tools import (
    # Code execution
    execute_python,
    execute_shell,
    # Code quality
    analyze_code,
    format_code,
    # Local Git operations (for local repo work)
    git_status,
    git_log,
    git_diff,
    git_commit,
    git_branch,
    git_checkout,
    git_pull,
    git_push,
    git_stash,
    # File operations
    read_file,
    write_file,
    # Research & docs
    web_search,
    search_documentation,
    scrape_webpage,
    # Project setup
    generate_gitignore,
    create_dockerfile,
    generate_readme,
    # Utilities
    json_parse,
    json_format,
)


# Base tools (always available)
BASE_TOOLS = [
    # Code execution
    execute_python,
    execute_shell,
    # Code quality
    analyze_code,
    format_code,
    # Local git
    git_status,
    git_log,
    git_diff,
    git_commit,
    git_branch,
    git_checkout,
    git_pull,
    git_push,
    git_stash,
    # Files
    read_file,
    write_file,
    # Research
    web_search,
    search_documentation,
    scrape_webpage,
    # Project setup
    generate_gitignore,
    create_dockerfile,
    generate_readme,
    # Utils
    json_parse,
    json_format,
]


def _get_github_mcp_instruction() -> str:
    """Return GitHub MCP instruction if available."""
    if os.getenv("GITHUB_TOKEN"):
        return """

    GITHUB MCP TOOLS (remote GitHub operations):
    - create_or_update_file: Create or update files in a repo
    - search_repositories: Search GitHub repositories
    - create_repository: Create a new repository
    - get_file_contents: Read files from a repo
    - push_files: Push multiple files at once
    - create_issue: Create GitHub issues
    - search_issues: Search issues and PRs
    - create_pull_request: Create pull requests
    - fork_repository: Fork a repository
    - create_branch: Create a new branch

    Use GitHub MCP for remote repo operations, local git tools for local work.
    """
    return ""


def create_developer_agent(mcp_tools: list[Any] | None = None):
    """
    Create developer agent with optional MCP tools.

    Args:
        mcp_tools: Optional list of MCP tools to include
    """
    tools = BASE_TOOLS.copy()
    if mcp_tools:
        tools.extend(mcp_tools)

    github_instruction = _get_github_mcp_instruction() if mcp_tools else ""

    return Agent(
        name="developer_agent",
        model=DEFAULT_MODEL,
        description="Senior software developer handling coding, debugging, code review, and GitHub operations",
        instruction=f"""
    You are a Senior Software Developer at AI Company. You are the technical expert
    responsible for all coding and development tasks.

    YOUR RESPONSIBILITIES:
    1. Write clean, efficient, and well-documented code
    2. Debug and fix issues in existing code
    3. Perform code reviews and suggest improvements
    4. Set up project structures and configurations
    5. Manage version control (local Git and GitHub)
    6. Create technical documentation
    7. Manage GitHub repositories, issues, and pull requests

    AVAILABLE TOOLS BY CATEGORY:

    Code Execution:
    - execute_python: Run Python code safely
    - execute_shell: Execute shell commands

    Code Quality:
    - analyze_code: Analyze code for issues and metrics
    - format_code: Format/prettify code
    - read_file/write_file: Read and write code files

    Local Git Operations:
    - git_status: Check repository status
    - git_log: View commit history
    - git_diff: See changes
    - git_commit: Create commits
    - git_branch: Manage branches
    - git_checkout: Switch branches
    - git_pull/git_push: Sync with remote
    - git_stash: Stash changes

    Project Setup:
    - generate_gitignore: Create .gitignore files
    - create_dockerfile: Generate Dockerfiles
    - generate_readme: Create README files

    Research:
    - search_documentation: Find programming docs
    - web_search: Search for solutions
    - scrape_webpage: Extract information from pages
    {github_instruction}
    CODING STANDARDS:
    - Follow language-specific best practices
    - Write meaningful commit messages
    - Document complex logic
    - Consider security implications
    - Write testable code

    Always explain your technical decisions and provide context for code changes.
    """,
        tools=tools,
    )


async def create_developer_agent_with_mcp():
    """Create developer agent with GitHub MCP tools loaded."""
    github_token = os.getenv("GITHUB_TOKEN")

    if github_token:
        try:
            tools, exit_stack = await MCPToolset.from_server(
                connection_params=StdioServerParameters(
                    command="npx",
                    args=["-y", "@modelcontextprotocol/server-github"],
                    env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token}
                )
            )
            print("✓ GitHub MCP tools loaded")
            return create_developer_agent(mcp_tools=tools), exit_stack
        except Exception as e:
            print(f"⚠ GitHub MCP failed to load: {e}")
            print("  Falling back to local git tools only")

    return create_developer_agent(), None


# Default agent (without MCP - for sync imports)
# Use create_developer_agent_with_mcp() for full GitHub integration
developer_agent = create_developer_agent()