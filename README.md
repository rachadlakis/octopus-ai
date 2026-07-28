# octopus-ai

A fresh A2A multi-agent project inspired by your original structure, but with new agent names and new roles.

## What is included

- 5 specialist agents, each exposed over A2A (HTTP)
- 1 orchestrator agent that controls all specialists via `AgentTool(RemoteA2aAgent(...))`
- 1 LoopAgent specialist (`risk_monitor_agent`)
- 1 SequentialAgent specialist (`planning_pipeline_agent`)
- Starter `requirements.txt`
- Starter `.env.example`
- `run_all_agents.py` script to launch all 5 specialist agents

## Architecture

```text
                                  A2A Protocol (HTTP)
                                         |
+-------------------------+              |
| orchestrator_agent      |              |
| (adk web on :8000)      |              |
|                         |   +----------+-------------------------------+
| AgentTool -> docs       +---> document_service_agent  (:8101)          |
| AgentTool -> planner    +---> planning_pipeline_agent (:8102) Sequential|
| AgentTool -> monitor    +---> risk_monitor_agent      (:8103) Loop      |
| AgentTool -> report     +---> reporting_agent         (:8104)           |
| AgentTool -> registry   +---> registry_agent          (:8105)           |
+-------------------------+   +------------------------------------------+
```

## Folder structure

```text
octopus-ai/
├── .env.example
├── README.md
├── requirements.txt
├── run_all_agents.py
├── orchestrator/
│   ├── __init__.py
│   └── agent.py
├── document_service_agent/
│   ├── __init__.py
│   └── document_service_agent.py
├── planning_pipeline_agent/
│   ├── __init__.py
│   └── planning_pipeline_agent.py
├── risk_monitor_agent/
│   ├── __init__.py
│   └── risk_monitor_agent.py
├── reporting_agent/
│   ├── __init__.py
│   └── reporting_agent.py
├── registry_agent/
│   ├── __init__.py
│   └── registry_agent.py
└── workspace/
```

## Agent roles

1. `document_service_agent` (port 8101)

- Sandboxed file operations (list/read/write/delete) for text files.

1. `planning_pipeline_agent` (port 8102)

- Sequential planning pipeline:
- Brief generation
- Plan generation
- QA/polish

1. `risk_monitor_agent` (port 8103)

- Loop-based iterative monitor:
- Inspector reviews report quality
- Improver refines report
- `finalize_cycle` exits loop when complete

1. `reporting_agent` (port 8104)

- Structured report generation using a markdown-report tool.

1. `registry_agent` (port 8105)

- Local JSON entity registry (add/list/search records).

## Setup

From `octopus-ai`:

```bash
pip install -r requirements.txt
copy .env.example .env
```

Set at least:

```env
ANTHROPIC_API_KEY=your_key_here
```

## Run

### Option A: Start all specialist agents together

```bash
python run_all_agents.py
```

Then in another terminal:

```bash
adk web .
```

Open [http://localhost:8000](http://localhost:8000) and select `orchestrator_agent`.

### Option B: Start agents manually

```bash
uvicorn document_service_agent.document_service_agent:a2a_app --host localhost --port 8101
uvicorn planning_pipeline_agent.planning_pipeline_agent:a2a_app --host localhost --port 8102
uvicorn risk_monitor_agent.risk_monitor_agent:a2a_app --host localhost --port 8103
uvicorn reporting_agent.reporting_agent:a2a_app --host localhost --port 8104
uvicorn registry_agent.registry_agent:a2a_app --host localhost --port 8105
adk web .
```

## Example prompts for orchestrator

- "Create a rollout plan for a new delivery zone and include risks."
- "Generate a monitoring report for this incident summary."
- "Save the final report to workspace/reports/zone_a.md"
- "Add driver Jane Doe with metadata to registry and list all driver records."
- "Plan, monitor, and produce a final markdown report for a fleet launch."
