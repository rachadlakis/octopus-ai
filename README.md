# AI Company

A multi-agent AI company simulation built with **Google ADK** (Agent Development Kit) and **A2A** (Agent-to-Agent Protocol). Each agent represents a company role with specialized tools.

## Company Structure

```
CEO (ceo_agent) - Port 9000
├── Developer (developer_agent) - Port 9001
│   └── Tools: code execution, git, GitHub MCP, documentation
├── Marketing (marketing_agent) - Port 9002
│   └── Tools: content analysis, social media, SEO, copywriting
└── HR (hr_agent) - Port 9003
    └── Tools: job posts, interviews, policies, onboarding
```

## Quick Start

### 1. Install Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set your model provider:
```bash
MODEL_PROVIDER=anthropic  # or openai, google
ANTHROPIC_API_KEY=your_key_here

# Optional: GitHub MCP for Developer agent
GITHUB_TOKEN=your_github_token
```

### 3. Run the Company

```bash
# Run the CEO (coordinates all departments)
python main.py ceo

# Or run individual agents
python main.py developer   # Port 9001
python main.py marketing   # Port 9002
python main.py hr          # Port 9003
```

### 4. Test the Agent

```bash
curl http://localhost:9000/.well-known/agent.json
```

## Agents & Tools

### CEO (Orchestrator)
Coordinates all departments using `AgentTool` to delegate while maintaining control.

### Developer
- **Code**: `execute_python`, `execute_shell`, `analyze_code`, `format_code`
- **Git**: `git_status`, `git_commit`, `git_branch`, `git_push`, etc.
- **GitHub MCP**: `create_issue`, `create_pull_request`, `search_repositories` (requires `GITHUB_TOKEN`)
- **Setup**: `generate_dockerfile`, `generate_readme`, `generate_gitignore`

### Marketing
- **Content**: `analyze_readability`, `analyze_headline`, `word_count`
- **Social**: `create_social_post`, `generate_hashtags`
- **SEO**: `seo_keyword_analysis`, `generate_cta`, `create_content_calendar`

### HR
- **Recruitment**: `generate_job_description`, `parse_resume`, `generate_interview_questions`
- **Onboarding**: `create_onboarding_checklist`
- **Policies**: `generate_policy_template`, `calculate_salary_range`

## Multi-Model Support

Uses **LiteLLM** via `google.adk.models.lite_llm` for provider flexibility:

| Provider | Models |
|----------|--------|
| Anthropic | claude-sonnet-4, claude-opus-4, claude-3.5-haiku |
| OpenAI | gpt-4o, gpt-4o-mini, o1 |
| Google | gemini-2.0-flash, gemini-1.5-pro |

## MCP Integration

Agents can connect to MCP (Model Context Protocol) servers for extended capabilities:

```python
from core import get_github_tools

# Load GitHub MCP tools
github_tools = await get_github_tools()
```

Available MCP integrations:
- **GitHub**: Issues, PRs, repositories
- **Slack**: Team communication
- **PostgreSQL**: Database queries
- **Filesystem**: File operations

## Technologies

- **Google ADK**: Agent Development Kit
- **A2A Protocol**: Agent-to-Agent communication
- **LiteLLM**: Multi-provider LLM support
- **MCP**: Model Context Protocol for tool integration
- **Uvicorn**: ASGI server

## License

MIT
