# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-agent AI company simulation built with **Google ADK** (Agent Development Kit) and **A2A** (Agent-to-Agent Protocol). Each agent represents a company role (CEO, Developer, Marketing, HR) with specialized tools for their domain.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run agents
python main.py ceo         # Port 9000 - CEO (orchestrates all departments)
python main.py developer   # Port 9001 - Software development
python main.py marketing   # Port 9002 - Marketing & content
python main.py hr          # Port 9003 - Human resources

# Test agent discovery
curl http://localhost:9000/.well-known/agent.json
```

## Company Structure

```
CEO (ceo_agent) - Port 9000
├── Developer (developer_agent) - Port 9001
│   └── Tools: code execution, git, file ops, documentation
├── Marketing (marketing_agent) - Port 9002
│   └── Tools: content analysis, social media, SEO, copywriting
└── HR (hr_agent) - Port 9003
    └── Tools: job posts, interviews, policies, onboarding
```

## Architecture

**Core Flow**: User → A2A Server → ADKAgentExecutor → ADK Agent → Response

- **CEO** (`agents/orchestrator.py`): Uses `AgentTool` to delegate to department heads while maintaining control flow.

- **ADKAgentExecutor** (`core/a2a_executor.py`): Bridge between ADK agents and A2A protocol.

## Key Pattern: AgentTool

Use `AgentTool(agent)` to delegate while keeping control:

```python
from google.adk.tools.agent_tool import AgentTool

ceo_agent = Agent(
    name="ceo_agent",
    tools=[
        AgentTool(developer_agent),  # Control returns after completion
        AgentTool(marketing_agent),
        AgentTool(hr_agent),
    ],
)
```

## Adding New Agents

1. Create `agents/new_agent/agent.py` with specialized tools
2. Export in `agents/__init__.py`
3. Add to CEO's tools: `AgentTool(new_agent)`
4. Add `run_new_agent()` in `server.py`
5. Add CLI option in `main.py`
6. Register port in `config/settings.py`

## Tools by Department

**Developer**: `execute_python`, `execute_shell`, `git_*`, `analyze_code`, `format_code`, `generate_dockerfile`, `generate_readme`

**Marketing**: `analyze_readability`, `create_social_post`, `generate_hashtags`, `seo_keyword_analysis`, `analyze_headline`, `create_content_calendar`

**HR**: `generate_job_description`, `parse_resume`, `generate_interview_questions`, `create_onboarding_checklist`, `calculate_salary_range`, `generate_policy_template`

## Environment

```bash
# Choose provider: anthropic, openai, or google
MODEL_PROVIDER=anthropic

# Set API key for your provider
ANTHROPIC_API_KEY=your_key_here
```

Uses `LiteLlm` from `google.adk.models.lite_llm` for multi-provider support.
