"""
AI Company - Web UI

A Streamlit-based interface for interacting with company agents.
Run with: streamlit run ui.py
"""
import asyncio
import streamlit as st
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Page config
st.set_page_config(
    page_title="AI Company",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .agent-card {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .ceo { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    .developer { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }
    .marketing { background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%); color: white; }
    .hr { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
    .testing { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; }
    .stChatMessage { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# Agent configurations
AGENTS = {
    "ceo": {
        "name": "CEO",
        "icon": "🏢",
        "color": "ceo",
        "description": "Chief Executive - Coordinates all departments",
        "port": 9000
    },
    "developer": {
        "name": "Developer",
        "icon": "💻",
        "color": "developer",
        "description": "Senior Software Developer - Code, Git, GitHub",
        "port": 9001
    },
    "marketing": {
        "name": "Marketing",
        "icon": "📢",
        "color": "marketing",
        "description": "Marketing Lead - Content, Social Media, SEO",
        "port": 9002
    },
    "hr": {
        "name": "HR",
        "icon": "👥",
        "color": "hr",
        "description": "HR Manager - Recruitment, Policies, Onboarding",
        "port": 9003
    },
    "testing": {
        "name": "Testing",
        "icon": "🧪",
        "color": "testing",
        "description": "QA Lead - Tests, Coverage, Quality",
        "port": 9004
    }
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


async def run_agent(agent, user_message: str, session_id: str):
    """Run agent and get response."""
    session_service = InMemorySessionService()

    runner = Runner(
        agent=agent,
        app_name=agent.name,
        session_service=session_service,
    )

    # Create session
    session = session_service.create_session(
        app_name=agent.name,
        user_id="ui_user",
        session_id=session_id,
        state={}
    )

    # Run agent
    response_text = ""
    async for event in runner.run(
        user_id="ui_user",
        session_id=session.id,
        new_message=user_message
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    response_text += part.text

    return response_text


def main():
    # Sidebar - Agent Selection
    with st.sidebar:
        st.markdown("# 🏢 AI Company")
        st.markdown("---")

        st.markdown("### Select Department")

        selected_agent = st.radio(
            "Choose an agent:",
            options=list(AGENTS.keys()),
            format_func=lambda x: f"{AGENTS[x]['icon']} {AGENTS[x]['name']}",
            label_visibility="collapsed"
        )

        st.markdown("---")

        # Agent info card
        agent_info = AGENTS[selected_agent]
        st.markdown(f"""
        <div class="agent-card {agent_info['color']}">
            <h3>{agent_info['icon']} {agent_info['name']}</h3>
            <p>{agent_info['description']}</p>
            <small>Port: {agent_info['port']}</small>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = f"session_{hash(str(st.session_state.get('session_counter', 0)))}"
            st.session_state.session_counter = st.session_state.get('session_counter', 0) + 1
            st.rerun()

        st.markdown("---")
        st.markdown("### Quick Actions")

        # Quick action buttons based on agent
        if selected_agent == "ceo":
            quick_actions = [
                "What can you help me with?",
                "Give me a company status report",
                "I need to hire a developer and have them build an API"
            ]
        elif selected_agent == "developer":
            quick_actions = [
                "Show git status",
                "Create a Python hello world",
                "Generate a Dockerfile for a FastAPI app"
            ]
        elif selected_agent == "marketing":
            quick_actions = [
                "Write a LinkedIn post about AI",
                "Analyze this headline: 'AI Changes Everything'",
                "Create hashtags for a tech startup"
            ]
        elif selected_agent == "hr":
            quick_actions = [
                "Create a job description for a Python developer",
                "Generate interview questions for a senior role",
                "Draft a remote work policy"
            ]
        elif selected_agent == "testing":
            quick_actions = [
                "Generate a pytest template",
                "What makes good test coverage?",
                "Create a mock template for a UserService class"
            ]

        for action in quick_actions:
            if st.button(action, use_container_width=True, key=f"quick_{action[:20]}"):
                st.session_state.pending_message = action
                st.rerun()

    # Main chat area
    agent_info = AGENTS[selected_agent]
    st.markdown(f"# {agent_info['icon']} Chat with {agent_info['name']}")
    st.markdown(f"*{agent_info['description']}*")
    st.markdown("---")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = "session_1"
    if "current_agent" not in st.session_state:
        st.session_state.current_agent = selected_agent

    # Reset chat if agent changed
    if st.session_state.current_agent != selected_agent:
        st.session_state.messages = []
        st.session_state.current_agent = selected_agent
        st.session_state.session_id = f"session_{selected_agent}"

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message.get("avatar")):
            st.markdown(message["content"])

    # Handle pending message from quick actions
    if "pending_message" in st.session_state:
        user_input = st.session_state.pending_message
        del st.session_state.pending_message
    else:
        user_input = st.chat_input(f"Message {agent_info['name']}...")

    if user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "avatar": "👤"
        })

        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Get agent response
        with st.chat_message("assistant", avatar=agent_info['icon']):
            with st.spinner(f"{agent_info['name']} is thinking..."):
                try:
                    agent = get_agent(selected_agent)
                    if agent:
                        response = asyncio.run(run_agent(
                            agent,
                            user_input,
                            st.session_state.session_id
                        ))
                    else:
                        response = "Error: Could not load agent."
                except Exception as e:
                    response = f"Error: {str(e)}"

                st.markdown(response)

        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "avatar": agent_info['icon']
        })

        st.rerun()


if __name__ == "__main__":
    main()
