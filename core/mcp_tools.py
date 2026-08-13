"""
MCP Tool Integration - Connect agents to MCP servers.

Provides factory functions to create MCP toolsets for different services.
"""
import os
from typing import Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters


async def get_github_tools(token: Optional[str] = None) -> MCPToolset:
    """
    Get GitHub MCP tools for repository management.

    Provides: create_issue, search_issues, create_pull_request,
              get_file_contents, push_files, search_repositories, etc.

    Args:
        token: GitHub personal access token (defaults to GITHUB_TOKEN env var)

    Returns:
        MCPToolset with GitHub tools
    """
    github_token = token or os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable required for GitHub MCP")

    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token}
        )
    )
    return tools


async def get_filesystem_tools(allowed_paths: list[str] = None) -> MCPToolset:
    """
    Get filesystem MCP tools for file operations.

    Provides: read_file, write_file, list_directory, search_files, etc.

    Args:
        allowed_paths: List of allowed directory paths (defaults to current dir)

    Returns:
        MCPToolset with filesystem tools
    """
    paths = allowed_paths or [os.getcwd()]

    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", *paths]
        )
    )
    return tools


async def get_slack_tools(token: Optional[str] = None) -> MCPToolset:
    """
    Get Slack MCP tools for team communication.

    Provides: send_message, read_channel, list_channels, etc.

    Args:
        token: Slack bot token (defaults to SLACK_BOT_TOKEN env var)

    Returns:
        MCPToolset with Slack tools
    """
    slack_token = token or os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        raise ValueError("SLACK_BOT_TOKEN environment variable required for Slack MCP")

    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-slack"],
            env={"SLACK_BOT_TOKEN": slack_token}
        )
    )
    return tools


async def get_postgres_tools(connection_string: Optional[str] = None) -> MCPToolset:
    """
    Get PostgreSQL MCP tools for database operations.

    Provides: query, list_tables, describe_table, etc.

    Args:
        connection_string: PostgreSQL connection string (defaults to DATABASE_URL env var)

    Returns:
        MCPToolset with PostgreSQL tools
    """
    db_url = connection_string or os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable required for PostgreSQL MCP")

    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-postgres", db_url]
        )
    )
    return tools


async def get_brave_search_tools(api_key: Optional[str] = None) -> MCPToolset:
    """
    Get Brave Search MCP tools for web search.

    Provides: brave_web_search, brave_local_search

    Args:
        api_key: Brave Search API key (defaults to BRAVE_API_KEY env var)

    Returns:
        MCPToolset with Brave Search tools
    """
    brave_key = api_key or os.getenv("BRAVE_API_KEY")
    if not brave_key:
        raise ValueError("BRAVE_API_KEY environment variable required for Brave Search MCP")

    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-brave-search"],
            env={"BRAVE_API_KEY": brave_key}
        )
    )
    return tools
