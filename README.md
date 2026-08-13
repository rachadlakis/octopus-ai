# AI Company

A multi-agent AI company simulation built with **Google ADK** (Agent Development Kit) and **A2A** (Agent-to-Agent Protocol). Each agent represents a company role with specialized tools.

## Company Structure

```
CEO (ceo_agent) - Port 9000
├── Developer (developer_agent) - Port 9001
│   └── Tools: code execution, git, GitHub MCP, documentation
├── Marketing (marketing_agent) - Port 9002
│   └── Tools: content analysis, social media, SEO, copywriting
├── HR (hr_agent) - Port 9003
│   └── Tools: job posts, interviews, policies, onboarding
└── Testing (testing_agent) - Port 9004
    └── Tools: pytest, jest, coverage, linting, test generation
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
python main.py testing     # Port 9004
```

### 4. Run the UI

**Option 1: Streamlit Web UI** (Recommended)
```bash
streamlit run ui.py
```
Opens a beautiful web interface at http://localhost:8501

**Option 2: ADK Web UI**
```bash
python run_adk_ui.py ceo      # or developer, marketing, hr, testing
```
Uses ADK's built-in web interface

**Option 3: Terminal Chat**
```bash
python chat.py ceo            # Simple terminal-based chat
```

**Option 4: A2A Server**
```bash
python main.py ceo            # Exposes agent via A2A protocol
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

### Testing/QA
- **Execution**: `run_pytest`, `run_unittest`, `run_jest`
- **Coverage**: `check_test_coverage`, `analyze_test_quality`
- **Generation**: `generate_test_template`, `create_mock_template`
- **Quality**: `lint_code`, `generate_test_report`

## Multi-Model Support

Uses **LiteLLM** via `google.adk.models.lite_llm` for provider flexibility:

| Provider | Models |
|----------|--------|
| Anthropic | claude-sonnet-4, claude-opus-4, claude-3.5-haiku |
| OpenAI | gpt-4o, gpt-4o-mini, o1 |
| Google | gemini-2.0-flash, gemini-1.5-pro |

## External Agent Integration (A2A)

Connect to agents from other frameworks (CrewAI, LangChain, AutoGen) via A2A protocol:

```python
from core import A2AClient

# Connect to any A2A-compliant agent
client = A2AClient("http://localhost:8080")
info = client.discover()  # Get agent capabilities
response = client.send("Hello from ADK!")
```

The CEO can also connect to external agents dynamically:
```
CEO: "Connect to the agent at localhost:8080 and ask it to analyze our data"
```

Tools available:
- `connect_to_external_agent(url)` - Discover external agent
- `call_external_agent(url, message)` - Send message to external agent
- `get_external_agent_skills(url)` - List external agent capabilities

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
