"""
A2A Agent Executor - bridges ADK agents with A2A protocol.

This executor wraps ADK agents to make them compatible with the
A2A (Agent-to-Agent) protocol standard.
"""
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


class ADKAgentExecutor(AgentExecutor):
    """
    Executor that bridges ADK agents with A2A protocol.

    This allows ADK agents to be exposed as A2A-compliant services
    that can be discovered and connected by other A2A clients.
    """

    def __init__(self, agent: Agent):
        """
        Initialize the executor with an ADK agent.

        Args:
            agent: The ADK Agent to execute
        """
        self.agent = agent
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=agent,
            app_name=agent.name,
            session_service=self.session_service,
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """
        Execute the agent with the given context.

        Args:
            context: Request context containing the message and metadata
            event_queue: Queue for sending events back to the client
        """
        try:
            user_message = self._extract_message(context)

            session_id = context.request_id
            user_id = "a2a_client"

            # Get or create session
            try:
                session = self.session_service.get_session(
                    app_name=self.agent.name,
                    user_id=user_id,
                    session_id=session_id
                )
            except Exception:
                session = self.session_service.create_session(
                    app_name=self.agent.name,
                    user_id=user_id,
                    session_id=session_id,
                    state={}
                )

            # Run the agent and collect response
            response_text = ""
            async for event in self.runner.run(
                user_id=user_id,
                session_id=session.id,
                new_message=user_message
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            response_text += part.text

            # Send response back through event queue (async)
            await event_queue.enqueue_event(new_agent_text_message(response_text))

        except Exception as e:
            error_msg = f"Error executing agent: {str(e)}"
            await event_queue.enqueue_event(new_agent_text_message(error_msg))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Cancel the current execution."""
        await event_queue.enqueue_event(
            new_agent_text_message("Task cancellation requested")
        )

    def _extract_message(self, context: RequestContext) -> str:
        """Extract the text message from the request context."""
        try:
            if hasattr(context, 'message') and context.message:
                message = context.message

                if hasattr(message, 'parts') and message.parts:
                    text_parts = []
                    for part in message.parts:
                        if hasattr(part, 'root') and hasattr(part.root, 'text'):
                            text_parts.append(part.root.text)
                        elif hasattr(part, 'text'):
                            text_parts.append(part.text)

                    if text_parts:
                        return " ".join(text_parts)

            return "Hello"
        except Exception as e:
            print(f"Error extracting message: {e}")
            return "Hello"
