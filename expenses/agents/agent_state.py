from typing import TypedDict, Literal, Optional
from dataclasses import dataclass, field

@dataclass
class AgentState(TypedDict):
    """State of the agent."""
    messages: list[dict]
    current_user_id: str
    selected_model: Literal['claude', 'openai', 'gemini', 'kimi']
    tool_calls: list[dict] = field(default_factory=list)
    last_error: Optional[str] = None
    step_count: int = 0
    max_steps: int = 10


@dataclass
class ToolResult:
    """Result of a tool call."""
    tool_name: str
    success: bool
    data: dict
    error: Optional[str] = None


@dataclass
class ToolCall:
    """Call to a tool."""
    tool_name: str
    args: dict
    result: ToolResult
    error: Optional[str] = None
